import time
import random
import os
import json
import redis
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import Refund, Payment, Order
from utils.errors import not_found

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
    time.sleep(TEST_PROCESSING_DELAY_MS / 1000)

    # -----------------------------
    # Random success/failure for test mode
    # -----------------------------
    success = True if DEFAULT_TEST_MODE else random.random() < 0.95

    if success:
        refund.status = "PROCESSED"
        # Optional: reduce payment.amount if tracking remaining balance
        # payment.amount -= refund.amount
    else:
        refund.status = "FAILED"
        refund.error_code = "REFUND_FAILED"
        refund.error_description = "Refund processing failed"

    db.commit()
    db.refresh(refund)

    # -----------------------------
    # Trigger webhook
    # -----------------------------
    webhook_payload = {
        "refund_id": refund.id,
        "payment_id": refund.payment_id,
        "merchant_id": refund.merchant_id,
        "amount": refund.amount,
        "status": refund.status,
        "reason": refund.reason,
        "error_code": refund.error_code,
        "error_description": refund.error_description,
    }

    redis_client.rpush(WEBHOOK_QUEUE, json.dumps(webhook_payload))