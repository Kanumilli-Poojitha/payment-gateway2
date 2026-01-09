import time
import random
import os
from datetime import datetime
from sqlalchemy.orm import Session

from models import Payment, Order, Merchant

DEFAULT_TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"
TEST_PROCESSING_DELAY = int(os.getenv("TEST_PROCESSING_DELAY", "500"))


def detect_card_network(card_number: str) -> str:
    if card_number.startswith("4"):
        return "visa"
    if card_number.startswith(("51", "52", "53", "54", "55")):
        return "mastercard"
    if card_number.startswith(("34", "37")):
        return "amex"
    return "unknown"


def process_payment(
    *,
    db: Session,
    payload: dict,
    merchant: Merchant | None = None,
    is_public: bool = False,
) -> Payment:
    order_id = payload.get("order_id")
    method = payload.get("method")
    test_mode = payload.get("test_mode", DEFAULT_TEST_MODE)

    # -------------------------
    # BASIC VALIDATION
    # -------------------------
    if not order_id:
        raise ValueError("order_id is required")

    if method not in ("upi", "card"):
        raise ValueError("Unsupported payment method")

    if method == "upi" and not payload.get("vpa"):
        raise ValueError("vpa is required for UPI payments")

    if method == "card" and not payload.get("card"):
        raise ValueError("card details are required for card payments")

    # -------------------------
    # FETCH ORDER
    # -------------------------
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ValueError("Order not found")

    # -------------------------
    # RESOLVE MERCHANT
    # -------------------------
    if is_public:
        merchant = db.query(Merchant).filter(
            Merchant.id == order.merchant_id
        ).first()
        if not merchant:
            raise ValueError("Merchant not found")
    else:
        if not merchant:
            raise ValueError("Merchant authentication required")
        if order.merchant_id != merchant.id:
            raise ValueError("Order does not belong to merchant")

    # -------------------------
    # PROCESS PAYMENT
    # -------------------------
    if test_mode:
        time.sleep(TEST_PROCESSING_DELAY / 1000)
        success = True
        prefix = "test_"
    else:
        prefix = "pay_"
        success = random.random() < (0.95 if method == "upi" else 0.9)

    card = payload.get("card")

    payment = Payment(
        id=f"{prefix}{order.id}_{int(time.time() * 1000)}",
        order_id=order.id,
        merchant_id=merchant.id,
        amount=order.amount,
        currency=order.currency,
        method=method,
        status="success" if success else "failed",
        vpa=payload.get("vpa") if method == "upi" else None,
        card_network=detect_card_network(card["number"]) if card else None,
        card_last4=card["number"][-4:] if card else None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    if not success:
        payment.error_code = "PAYMENT_FAILED"
        payment.error_description = "Payment authorization failed"

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment