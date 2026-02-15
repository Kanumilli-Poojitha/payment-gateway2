import os
import json
import redis
import requests
import signal
import time
import threading
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import hmac
import hashlib

from models import Merchant, Webhook, WebhookLog
from database import Base

# -----------------------------
# Config
# -----------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
QUEUE_NAME = os.getenv("WEBHOOK_QUEUE", "gateway_webhooks")
DATABASE_URL = os.getenv("DATABASE_URL")
WEBHOOK_RETRY_INTERVALS_TEST = os.getenv("WEBHOOK_RETRY_INTERVALS_TEST", "true").lower() == "true"

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

running = True

# -----------------------------
# Retry Intervals
# -----------------------------
PROD_RETRY_INTERVALS = [0, 60, 300, 1800, 7200]  # seconds
TEST_RETRY_INTERVALS = [0, 5, 10, 15, 20]     # seconds

def get_retry_delay(attempt: int) -> int:
    intervals = TEST_RETRY_INTERVALS if WEBHOOK_RETRY_INTERVALS_TEST else PROD_RETRY_INTERVALS
    if attempt < len(intervals):
        return intervals[attempt]
    return -1

# -----------------------------
# Signature Logic
# -----------------------------
def generate_signature(secret: str, payload_str: str) -> str:
    return hmac.new(
        key=secret.encode(),
        msg=payload_str.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

# -----------------------------
# Delivery Logic
# -----------------------------
def deliver_webhook(db, log_id: str):
    log = db.query(WebhookLog).filter(WebhookLog.id == log_id).first()
    if not log:
        return

    # Fetch merchant for URL and Secret
    # Use merchant_id from log
    merchant = db.query(Merchant).filter(Merchant.id == log.merchant_id).first()
    
    # Requirement says fetch merchant details: retrieve webhook_url (must be configured)
    # Since we have multiple webhooks in the 'webhooks' table, let's find the one matching the event or all.
    # Actually, the register_webhook router stores them in 'webhooks' table.
    # Let's assume we use the first active webhook for that merchant or all.
    # The requirement says "retrieve webhook_url (skip if NULL)".
    
    webhooks = db.query(Webhook).filter(Webhook.merchant_id == log.merchant_id, Webhook.active == True).all()
    if not webhooks:
        log.status = "failed"
        log.response_body = "No active webhooks configured for merchant"
        db.commit()
        return

    # In this implementation, we log/retry for each webhook if there are multiple.
    # But current WebhookLog schema has merchant_id instead of webhook_id (per requirement).
    # So we'll iterate and send to all. (For simplicity, usually we'd have one log per delivery attempt).
    
    payload_str = json.dumps(log.payload, separators=(",", ":"))
    
    overall_success = True
    for webhook in webhooks:
        signature = generate_signature(webhook.secret, payload_str)
        
        try:
            print(f"📡 Delivering webhook {log.id} to {webhook.url} (Attempt {log.attempts + 1})")
            resp = requests.post(
                webhook.url,
                data=payload_str,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature
                },
                timeout=5
            )
            log.response_code = resp.status_code
            log.response_body = resp.text[:1000] # Truncate if too long
            
            if 200 <= resp.status_code < 300:
                print(f"✅ Webhook {log.id} SUCCESS")
            else:
                print(f"❌ Webhook {log.id} FAILED with {resp.status_code}")
                overall_success = False
        except Exception as e:
            print(f"⚠️ Webhook {log.id} ERROR: {e}")
            log.response_body = str(e)
            overall_success = False

    log.attempts += 1
    log.last_attempt_at = datetime.utcnow()

    if overall_success:
        log.status = "success"
        log.next_retry_at = None
    else:
        delay = get_retry_delay(log.attempts)
        if delay >= 0:
            log.status = "pending"
            log.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
            print(f"🔁 Scheduled retry for {log.id} in {delay}s")
        else:
            log.status = "failed"
            log.next_retry_at = None
            print(f"🛑 Webhook {log.id} permanently failed after 5 attempts")

    db.commit()

# -----------------------------
# Worker Loops
# -----------------------------
def retry_scheduler():
    print("⏲️ Webhook retry scheduler started")
    while running:
        db = SessionLocal()
        try:
            # Poll for pending logs that are due
            pending_logs = db.query(WebhookLog).filter(
                WebhookLog.status == "pending",
                WebhookLog.next_retry_at <= datetime.utcnow()
            ).limit(10).all()

            for log in pending_logs:
                deliver_webhook(db, log.id)
        except Exception as e:
            print(f"⚠️ Scheduler error: {e}")
        finally:
            db.close()
        time.sleep(5)

def worker_loop():
    print("🟢 Webhook worker started")
    # Start scheduler thread
    scheduler = threading.Thread(target=retry_scheduler, daemon=True)
    scheduler.start()

    while running:
        item = redis_client.blpop(QUEUE_NAME, timeout=5)
        if not item:
            continue

        _, payload = item
        try:
            job = json.loads(payload)
            merchant_id = job.get("merchant_id")
            event = job.get("event")
            data_payload = job.get("payload")

            if not merchant_id:
                print("❌ Missing merchant_id in job")
                continue

            db = SessionLocal()
            try:
                # Create initial log
                log = WebhookLog(
                    merchant_id=merchant_id,
                    event=event,
                    payload=data_payload,
                    status="pending",
                    attempts=0,
                    next_retry_at=datetime.utcnow() # Immediate
                )
                db.add(log)
                db.commit()
                db.refresh(log)

                # Process immediately
                deliver_webhook(db, log.id)
            finally:
                db.close()

        except Exception as e:
            print(f"⚠️ Webhook worker error: {e}")

def graceful_shutdown(signum, frame):
    global running
    print("🛑 Webhook worker shutting down...")
    running = False

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

if __name__ == "__main__":
    try:
        from migrate import migrate
        migrate()
    except Exception as e:
        print(f"⚠️ Migration failed: {e}")
    worker_loop()