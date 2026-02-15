from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models import Payment, Refund
from auth import authenticate
from schemas.refund import RefundCreate, RefundResponse
from utils import generate_id
from utils.idempotency import get_existing_response, save_idempotency_response
import redis, os, json

# -----------------------------
# Redis config
# -----------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
REFUND_QUEUE = os.getenv("REFUND_QUEUE", "gateway_refunds")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

router = APIRouter(prefix="/refunds", tags=["refunds"])


# -----------------------------
# CREATE REFUND (ASYNC)
# -----------------------------
@router.post("", response_model=RefundResponse, status_code=201)
def create_refund(
    data: RefundCreate,
    merchant=Depends(authenticate),
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key")
):
    # -----------------------------
    # Idempotency: prevent double refund
    # -----------------------------
    if idempotency_key:
        cached = get_existing_response(db, merchant.id, idempotency_key, data.dict())
        if cached:
            from fastapi.responses import JSONResponse
            return JSONResponse(content=cached["body"], status_code=cached["status_code"])

    # -----------------------------
    # Validate payment exists and belongs to merchant
    # -----------------------------
    payment = db.query(Payment).filter_by(
        id=data.payment_id,
        merchant_id=merchant.id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Optional: prevent cumulative over-refund
    refunded_total = (
        db.query(Refund)
        .filter(Refund.payment_id == payment.id, Refund.status != "FAILED")
        .with_entities(func.coalesce(func.sum(Refund.amount), 0))
        .scalar()
    )

    if data.amount + refunded_total > payment.amount:
        raise HTTPException(
            status_code=400,
            detail="Refund amount exceeds payment amount"
        )

    # -----------------------------
    # Create refund record
    # -----------------------------
    refund = Refund(
        id=generate_id("refund_"),
        payment_id=payment.id,
        merchant_id=merchant.id,
        amount=data.amount,
        status="pending",
        reason=data.reason
    )

    db.add(refund)
    db.commit()
    db.refresh(refund)

    # -----------------------------
    # Enqueue async refund job
    # -----------------------------
    redis_client.rpush(
        REFUND_QUEUE,
        json.dumps({"refund_id": refund.id})
    )

    # -----------------------------
    # Save idempotency response
    # -----------------------------
    from schemas.refund import RefundResponse
    response_data = RefundResponse.from_orm(refund).dict()
    if idempotency_key:
        save_idempotency_response(db, merchant.id, idempotency_key, data.dict(), response_data, 201)

    return response_data


# -----------------------------
# GET REFUND
# -----------------------------
@router.get("/{refund_id}", response_model=RefundResponse)
def get_refund(
    refund_id: str,
    merchant=Depends(authenticate),
    db: Session = Depends(get_db)
):
    refund = db.query(Refund).filter_by(
        id=refund_id,
        merchant_id=merchant.id
    ).first()

    if not refund:
        raise HTTPException(status_code=404, detail="Refund not found")

    return refund