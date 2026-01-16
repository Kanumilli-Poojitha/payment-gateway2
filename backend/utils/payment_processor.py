import time
import random
import os
import json
import redis
from sqlalchemy.orm import Session

from models import Payment, Order
from utils.errors import not_found, bad_request
from utils import generate_id

# -----------------------------
# Config
# -----------------------------
DEFAULT_TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"
TEST_PROCESSING_DELAY_MS = int(os.getenv("TEST_PROCESSING_DELAY", "500"))

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
WEBHOOK_QUEUE = os.getenv("WEBHOOK_QUEUE", "gateway_webhooks")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# =====================================================
# ✅ API-SIDE FUNCTION (required for imports)
# =====================================================
def process_payment(
    db: Session,
    payload: dict,
    merchant=None,
    is_public: bool = False,
    idempotency_key: str | None = None,
):
    """
    Creates a payment record ONLY.
    Actual processing happens in async worker.
    """

    order = db.query(Order).filter(Order.id == payload["order_id"]).first()
    if not order:
        not_found("Order not found")

    if order.status.lower() == "paid":
        bad_request("Order already paid")

    payment = Payment(
        id=generate_id("pay_"),
        order_id=order.id,
        merchant_id=merchant.id if merchant else None,
        amount=order.amount,
        currency=order.currency,
        method=payload.get("method"),
        status="CREATED",
        vpa=payload.get("vpa"),
        idempotency_key=idempotency_key,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


# =====================================================
# ✅ WORKER-SIDE FUNCTION (async processor)
# =====================================================
def process_payment_job(db: Session, payment_id: str):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise ValueError(f"Payment {payment_id} not found")

    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if not order:
        raise ValueError("Order not found")

    # simulate async delay
    time.sleep(TEST_PROCESSING_DELAY_MS / 1000)

    success = True if DEFAULT_TEST_MODE else random.random() < 0.95

    if success:
        payment.status = "SUCCESS"
        order.status = "PAID"
    else:
        payment.status = "FAILED"
        payment.error_code = "PAYMENT_FAILED"
        payment.error_description = "Authorization failed"
        order.status = "FAILED"

    db.commit()


    # enqueue webhook AFTER final state
    job = {
        "payment_id": payment.id,
        "event_type": f"payment.{payment.status.lower()}",
        "amount": payment.amount,
        "currency": payment.currency,
        "method": payment.method,
        "order_id": payment.order_id,
        "merchant_id": payment.merchant_id,
    }

    redis_client.rpush(WEBHOOK_QUEUE, json.dumps(job))