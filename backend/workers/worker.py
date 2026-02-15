import os
import time
import redis
import json
import random
import signal
from sqlalchemy.orm import Session
from database import SessionLocal
from models.payment import Payment
from models.order import Order

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
QUEUE_NAME = os.getenv("WORKER_QUEUE", "gateway_jobs")
DLQ_QUEUE = os.getenv("DLQ_QUEUE", "gateway_jobs_dlq")
WEBHOOK_QUEUE = os.getenv("WEBHOOK_QUEUE", "gateway_webhooks")

MAX_RETRIES = int(os.getenv("WORKER_MAX_RETRIES", "3"))
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"
TEST_PROCESSING_DELAY = int(os.getenv("TEST_PROCESSING_DELAY", "1000"))
TEST_PAYMENT_SUCCESS = os.getenv("TEST_PAYMENT_SUCCESS", "true").lower() == "true"

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
running = True


def graceful_shutdown(signum, frame):
    global running
    print("🛑 Payment worker shutting down...")
    running = False


signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)


def process_payment(payment_id: str) -> bool:
    db: Session = SessionLocal()
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            print(f"❌ Payment {payment_id} not found")
            return False

        order = db.query(Order).filter(Order.id == payment.order_id).first()
        if not order:
            print(f"❌ Order {payment.order_id} not found")
            return False

        payment.status = "PROCESSING"
        db.commit()
        print(f"⚙️ Processing payment {payment.id}")

        # -----------------------------
        # Delay
        # -----------------------------
        if TEST_MODE:
            time.sleep(TEST_PROCESSING_DELAY / 1000)
        else:
            time.sleep(random.uniform(5, 10))

        # -----------------------------
        # Outcome
        # -----------------------------
        if TEST_MODE:
            success = TEST_PAYMENT_SUCCESS
        else:
            rate = 0.90 if payment.method == "upi" else 0.95
            success = random.random() < rate

        if success:
            payment.status = "success" # requirement says success/failed lowercase
            order.status = "paid"
            print(f"✅ Payment {payment.id} SUCCESS")
        else:
            payment.status = "failed"
            payment.error_code = "PAYMENT_FAILED"
            payment.error_description = "Authorization failed"
            order.status = "failed"
            print(f"❌ Payment {payment.id} FAILED")

        db.commit()

        # -----------------------------
        # Enqueue Webhook
        # -----------------------------
        webhook_payload = {
            "event": f"payment.{payment.status}",
            "timestamp": int(time.time()),
            "data": {
                "payment": {
                    "id": payment.id,
                    "order_id": payment.order_id,
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "method": payment.method,
                    "vpa": payment.vpa,
                    "status": payment.status,
                    "created_at": payment.created_at.isoformat() if payment.created_at else None,
                }
            }
        }

        redis_client.rpush(WEBHOOK_QUEUE, json.dumps({
            "merchant_id": payment.merchant_id,
            "event": f"payment.{payment.status}",
            "payload": webhook_payload
        }))

        return success
    finally:
        db.close()


def worker_loop():
    print("🟢 Payment worker started")
    while running:
        item = redis_client.blpop(QUEUE_NAME, timeout=5)
        if not item:
            continue

        _, payload = item

        try:
            job = json.loads(payload)
        except json.JSONDecodeError:
            redis_client.rpush(DLQ_QUEUE, payload)
            continue

        payment_id = job.get("payment_id")
        retries = job.get("retries", 0)

        if not payment_id:
            redis_client.rpush(DLQ_QUEUE, payload)
            continue

        success = process_payment(payment_id)

        if not success:
            if retries < MAX_RETRIES:
                job["retries"] = retries + 1
                redis_client.rpush(QUEUE_NAME, json.dumps(job))
                print(f"🔁 Retry {job['retries']} for payment {payment_id}")
            else:
                redis_client.rpush(DLQ_QUEUE, json.dumps(job))
                print(f"⚠️ Payment {payment_id} moved to DLQ")


if __name__ == "__main__":
    from migrate import migrate
    migrate()
    worker_loop()