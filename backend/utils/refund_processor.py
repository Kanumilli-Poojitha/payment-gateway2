import time
import random
import os
import json
import redis
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from models import Refund, Payment, Order

# -----------------------------
# Config
# -----------------------------
DEFAULT_TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"
TEST_PROCESSING_DELAY_MS = int(os.getenv("TEST_PROCESSING_DELAY", "500"))

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
REFUND_QUEUE = os.getenv("REFUND_QUEUE", "gateway_refunds")
WEBHOOK_QUEUE = os.getenv("WEBHOOK_QUEUE", "gateway_webhooks")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# =====================================================
# Worker: process refund
# =====================================================
def process_refund_job(db: Session, refund_id: str):
    refund = db.query(Refund).filter(Refund.id == refund_id).first()
    if not refund:
        raise ValueError(f"Refund {refund_id} not found")

    payment = db.query(Payment).filter(Payment.id == refund.payment_id).first()
    if not payment:
        raise ValueError("Payment not found")

    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if not order:
        raise ValueError("Order not found")

    # -----------------------------
    # Simulate async delay
    # -----------------------------
    if DEFAULT_TEST_MODE:
        time.sleep(TEST_PROCESSING_DELAY_MS / 1000)
    else:
        time.sleep(random.uniform(3, 5))

    # -----------------------------
    # Outcome
    # -----------------------------
    refund.status = "processed"
    refund.processed_at = datetime.utcnow()

    db.commit()
    db.refresh(refund)

    # -----------------------------
    # Trigger webhook
    # -----------------------------
    webhook_payload = {
        "event": "refund.processed",
        "timestamp": int(time.time()),
        "data": {
            "refund": {
                "id": refund.id,
                "payment_id": refund.payment_id,
                "amount": refund.amount,
                "reason": refund.reason,
                "status": refund.status,
                "created_at": refund.created_at.isoformat() if refund.created_at else None,
                "processed_at": refund.processed_at.isoformat() if refund.processed_at else None,
            }
        }
    }

    redis_client.rpush(WEBHOOK_QUEUE, json.dumps({
        "merchant_id": refund.merchant_id,
        "event": "refund.processed",
        "payload": webhook_payload
    }))