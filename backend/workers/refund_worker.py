import os
import json
import time
import redis
from sqlalchemy.orm import Session
from database import SessionLocal
from utils.refund_processor import process_refund_job

# -----------------------------
# Redis config
# -----------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
REFUND_QUEUE = os.getenv("REFUND_QUEUE", "gateway_refunds")
DLQ_QUEUE = os.getenv("REFUND_DLQ_QUEUE", "gateway_refunds_dlq")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# -----------------------------
# Worker loop
# -----------------------------
def worker_loop():
    print("🟢 Refund worker started")
    while True:
        item = redis_client.blpop(REFUND_QUEUE, timeout=5)
        if not item:
            continue

        _, payload = item
        try:
            job = json.loads(payload)
            refund_id = job.get("refund_id")
            if not refund_id:
                raise ValueError("Missing refund_id in job payload")

            # -----------------------------
            # Process refund
            # -----------------------------
            db: Session = SessionLocal()
            try:
                process_refund_job(db, refund_id)
            finally:
                db.close()

        except Exception as e:
            print(f"⚠️ Failed to process refund job: {e}")
            redis_client.rpush(DLQ_QUEUE, payload)
            continue


if __name__ == "__main__":
    try:
        from migrate import migrate
        migrate()
    except Exception:
        pass
    worker_loop()