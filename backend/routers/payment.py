from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Payment
from schemas.payment import PaymentCreate, PaymentResponse
from auth import authenticate
from utils.errors import bad_request, not_found, internal_error
from utils.payment_processor import process_payment

router = APIRouter(prefix="/payments", tags=["payments"])


# =================================================
# MERCHANT AUTHENTICATED PAYMENT (DASHBOARD / API)
# =================================================
@router.post("", response_model=PaymentResponse, status_code=201)
def create_payment(
    data: PaymentCreate,
    merchant=Depends(authenticate),
    db: Session = Depends(get_db),
):
    try:
        return process_payment(
            db=db,
            merchant=merchant,
            payload=data.dict(exclude_none=True),
        )

    except ValueError as e:
        message = str(e)
        if "not found" in message.lower():
            not_found(message)
        bad_request(message)

    except Exception:
        internal_error()

# =================================================
# GET PAYMENT STATUS (MERCHANT)
# =================================================
@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment_status(
    payment_id: str,
    merchant=Depends(authenticate),
    db: Session = Depends(get_db),
):
    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id,
            Payment.merchant_id == merchant.id,
        )
        .first()
    )

    if not payment:
        not_found("Payment not found")

    return payment


# =================================================
# LIST PAYMENTS (MERCHANT)
# =================================================
@router.get("", response_model=list[PaymentResponse])
def list_payments(
    merchant=Depends(authenticate),
    db: Session = Depends(get_db),
):
    return (
        db.query(Payment)
        .filter(Payment.merchant_id == merchant.id)
        .order_by(Payment.created_at.desc())
        .all()
    )