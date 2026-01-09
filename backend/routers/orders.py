from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Order
from utils import generate_id
from auth import authenticate
from schemas.order import OrderCreate, OrderResponse

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

# -----------------------------
# CREATE ORDER (MERCHANT)
# -----------------------------
@router.post("", response_model=OrderResponse, status_code=201)
def create_order(
    data: OrderCreate,
    merchant=Depends(authenticate),
    db: Session = Depends(get_db)
):
    if data.amount < 100:
        raise HTTPException(400, "amount must be at least 100")

    order = Order(
        id=generate_id("order_"),
        merchant_id=merchant.id,
        amount=data.amount,
        currency=data.currency,
        receipt=data.receipt,
        notes=data.notes,
        status="created"
    )

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


# -----------------------------
# GET ORDER (MERCHANT)
# -----------------------------
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    merchant=Depends(authenticate),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter_by(
        id=order_id,
        merchant_id=merchant.id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    return order