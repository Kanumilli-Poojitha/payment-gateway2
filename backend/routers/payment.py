from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
import json, redis
from datetime import datetime

from database import get_db
from models import Payment, Order
from schemas import PaymentCreate, PaymentResponse, CaptureRequest
from auth import authenticate
from utils import generate_id
from utils.errors import not_found
from utils.idempotency import get_existing_response, save_idempotency_response

router = APIRouter(prefix="/payments", tags=["Payments"])

REDIS_URL = "redis://redis:6379"
QUEUE_NAME = "gateway_jobs"
WEBHOOK_QUEUE = "gateway_webhooks"

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


@router.post("", response_model=PaymentResponse, status_code=201)
def create_payment(
    data: PaymentCreate,
    merchant=Depends(authenticate),
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
):
    if idempotency_key:
        cached = get_existing_response(db, merchant.id, idempotency_key, data.dict())
        if cached:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content=cached["body"],
                status_code=cached["status_code"]
            )
    order = db.query(Order).filter_by(id=data.order_id).first()
    if not order:
        not_found("Order not found")

    payment = Payment(
        id=generate_id("pay_"),
        order_id=order.id,
        merchant_id=merchant.id,
        amount=order.amount,
        currency=order.currency,
        method=data.method,
        status="pending",
        captured=False,
        vpa=data.vpa,
        idempotency_key=idempotency_key,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    redis_client.rpush(QUEUE_NAME, json.dumps({"payment_id": payment.id}))

    # Prepare response for pydantic validation and saving
    from schemas import PaymentResponse
    response_data = PaymentResponse.from_orm(payment).model_dump()

    if idempotency_key:
        save_idempotency_response(db, merchant.id, idempotency_key, data.dict(), response_data, 201)

    return response_data


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: str, merchant=Depends(authenticate), db: Session = Depends(get_db)):
    payment = db.query(Payment).filter_by(id=payment_id, merchant_id=merchant.id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.post("/{payment_id}/capture", response_model=PaymentResponse)
def capture_payment(
    payment_id: str,
    payload: CaptureRequest,
    merchant=Depends(authenticate),
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
):
    # 🔒 Idempotency check
    if idempotency_key:
        cached = get_existing_response(
            db=db,
            merchant_id=merchant.id,
            idem_key=idempotency_key,
            request_payload={"payment_id": payment_id, **payload.dict()},
        )
        if cached:
            from fastapi.responses import JSONResponse
            return JSONResponse(content=cached["body"], status_code=cached["status_code"])

    payment = db.query(Payment).filter_by(
        id=payment_id, merchant_id=merchant.id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status != "success":
        raise HTTPException(status_code=400, detail="Payment not in capturable state")

    if payment.captured:
        response = PaymentResponse.from_orm(payment).dict()
        if idempotency_key:
            save_idempotency_response(
                db,
                merchant.id,
                idempotency_key,
                {"payment_id": payment_id, **payload.dict()},
                response,
                200,
            )
        return payment

    payment.captured = True
    payment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(payment)

    redis_client.rpush(WEBHOOK_QUEUE, json.dumps({
        "payment_id": payment.id,
        "event_type": "payment.captured",
        "order_id": payment.order_id,
        "merchant_id": payment.merchant_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "method": payment.method,
    }))

    response = PaymentResponse.from_orm(payment).dict()

    if idempotency_key:
        save_idempotency_response(
            db,
            merchant.id,
            idempotency_key,
            {"payment_id": payment_id, **payload.dict()},
            response,
            200,
        )

    return payment