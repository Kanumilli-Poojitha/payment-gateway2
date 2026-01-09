# backend/services.py
import time
import random
from sqlalchemy.orm import Session

from models import Merchant, Order, Payment
from utils.validation import (
    validate_vpa,
    luhn_check,
    detect_card_network,
    validate_expiry,
)
from utils.helpers import generate_id
from config import (
    TEST_MODE,
    TEST_PAYMENT_SUCCESS,
    TEST_PROCESSING_DELAY,
    UPI_SUCCESS_RATE,
    CARD_SUCCESS_RATE,
)

# ---------- AUTH ----------

def authenticate_merchant(db: Session, api_key: str, api_secret: str):
    return (
        db.query(Merchant)
        .filter(
            Merchant.api_key == api_key,
            Merchant.api_secret == api_secret,
            Merchant.is_active == True,
        )
        .first()
    )

# ---------- PAYMENTS ----------

def process_payment(db: Session, merchant: Merchant, payload: dict):
    order = (
        db.query(Order)
        .filter(
            Order.id == payload["order_id"],
            Order.merchant_id == merchant.id,
        )
        .first()
    )

    if not order:
        raise LookupError("Order not found")

    payment = Payment(
        id=generate_id("pay_"),
        order_id=order.id,
        merchant_id=merchant.id,
        amount=order.amount,
        currency=order.currency,
        method=payload["method"],
        status="processing",
    )

    # ---- METHOD VALIDATION ----
    if payload["method"] == "upi":
        if not validate_vpa(payload.get("vpa", "")):
            raise ValueError("Invalid VPA")
        payment.vpa = payload["vpa"]
        success_rate = UPI_SUCCESS_RATE

    elif payload["method"] == "card":
        card = payload.get("card")
        if not card:
            raise ValueError("Invalid card details")

        if not luhn_check(card["number"]):
            raise ValueError("Invalid card number")

        if not validate_expiry(card["expiry_month"], card["expiry_year"]):
            raise ValueError("Card expired")

        payment.card_network = detect_card_network(card["number"])
        payment.card_last4 = card["number"][-4:]
        success_rate = CARD_SUCCESS_RATE

    else:
        raise ValueError("Invalid payment method")

    db.add(payment)
    db.commit()
    db.refresh(payment)

    # ---- PROCESSING ----
    if TEST_MODE:
        time.sleep(TEST_PROCESSING_DELAY / 1000)
        success = TEST_PAYMENT_SUCCESS
    else:
        time.sleep(random.uniform(0.8, 1.5))
        success = random.random() < success_rate

    if success:
        payment.status = "success"
        order.status = "paid"
    else:
        payment.status = "failed"
        payment.error_code = "PAYMENT_FAILED"
        payment.error_description = "Payment processing failed"

    db.commit()
    db.refresh(payment)

    return payment