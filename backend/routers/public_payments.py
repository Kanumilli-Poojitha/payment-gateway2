from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Payment   # ✅ MISSING IMPORT (IMPORTANT)
from schemas.payment import PaymentCreate, PaymentResponse
from utils.payment_processor import process_payment
from utils.errors import bad_request, not_found

router = APIRouter(
    prefix="/payments/public",
    tags=["public-payments"]
)

# ==============================
# CREATE PUBLIC PAYMENT (POST)
# ==============================
@router.post("", response_model=PaymentResponse, status_code=201)
def create_public_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
):
    try:
        return process_payment(
            db=db,
            payload=data.dict(exclude_none=True),
            merchant=None,
            is_public=True,
        )

    except ValueError as e:
        message = str(e)
        if "not found" in message.lower():
            return not_found(message)
        return bad_request(message)

# ==============================
# GET PUBLIC PAYMENT STATUS (GET)
# ==============================
@router.get("/{payment_id}", response_model=PaymentResponse)
def get_public_payment_status(
    payment_id: str,
    db: Session = Depends(get_db),
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        return not_found("Payment not found")
    return payment