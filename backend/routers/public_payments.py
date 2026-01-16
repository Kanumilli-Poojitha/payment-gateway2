from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
import redis, json, os

from database import get_db
from models import Payment, Order, Merchant
from schemas import PaymentCreate, PaymentResponse
from utils import generate_id
from utils.errors import not_found

router = APIRouter(prefix="/payments/public", tags=["public-payments"])

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
QUEUE_NAME = os.getenv("WORKER_QUEUE", "gateway_jobs")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# -----------------------------
# CREATE PUBLIC PAYMENT
# -----------------------------
@router.post("", response_model=PaymentResponse, status_code=201)
def create_public_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
):
    order = db.query(Order).filter_by(id=data.order_id).first()
    if not order:
        not_found("Order not found")

    merchant = db.query(Merchant).filter_by(id=order.merchant_id).first()
    if not merchant:
        not_found("Merchant not found")

    payment = Payment(
        id=generate_id("pay_"),
        order_id=order.id,
        merchant_id=merchant.id,
        amount=order.amount,
        currency=order.currency,
        method=data.method,
        status="CREATED",
        captured=False,
        vpa=data.vpa,
        idempotency_key=idempotency_key,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    # enqueue async processing
    redis_client.rpush(QUEUE_NAME, json.dumps({"payment_id": payment.id}))

    return PaymentResponse.from_orm(payment)

# -----------------------------
# GET PUBLIC PAYMENT STATUS
# -----------------------------
@router.get("/{payment_id}", response_model=PaymentResponse)
def get_public_payment(payment_id: str, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter_by(id=payment_id).first()
    if not payment:
        raise HTTPException(404, "Payment not found")
    return PaymentResponse.from_orm(payment)