import os
import time
import json
import logging
from datetime import datetime, timedelta

import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError, OperationalError

from models.payment import Payment
from models.reconciliation import PaymentLog

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
PROCESSING_THRESHOLD = int(os.getenv("PROCESSING_THRESHOLD_SEC", "300"))

ALERT_QUEUE = "gateway_alerts"
WORKER_ID = "reconciliation_worker"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def reconcile_payments():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        stuck_threshold = now - timedelta(seconds=PROCESSING_THRESHOLD)

        payments = db.query(Payment).filter(
            Payment.status == "PROCESSING",
            Payment.updated_at < stuck_threshold
        ).all()

        if not payments:
            return

        for payment in payments:
            old_status = payment.status
            payment.status = "FAILED"
            payment.error_code = "STUCK_PROCESSING"
            payment.error_description = "Payment stuck in PROCESSING beyond threshold"
            db.commit()

            log = PaymentLog(payment_id=payment.id, old_status=old_status, new_status=payment.status, worker_id=WORKER_ID)
            db.add(log)
            db.commit()

            redis_client.rpush(ALERT_QUEUE, json.dumps({
                "payment_id": payment.id,
                "issue": "stuck_processing",
                "timestamp": datetime.utcnow().isoformat()
            }))

            logging.warning(f"Reconciled stuck payment {payment.id}")
    finally:
        db.close()

def worker_loop():
    logging.info("🟢 Reconciliation worker started")
    while True:
        try:
            reconcile_payments()
        except (ProgrammingError, OperationalError):
            logging.warning("DB not ready yet, retrying...")
        except Exception:
            logging.exception("Unexpected reconciliation error")
        time.sleep(60)

if __name__ == "__main__":
    try:
        import sys
        import os
        sys.path.append(os.getcwd())
        from migrate import migrate
        migrate()
    except Exception:
        pass
    worker_loop()