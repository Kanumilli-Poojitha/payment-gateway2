from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random
import string

from database import get_db
from models import Order, Merchant
from schemas.order import OrderCreate, OrderResponse

router = APIRouter(
    prefix="/orders/public",
    tags=["public-orders"],
)


def generate_order_id() -> str:
    return "order_" + "".join(
        random.choices(string.ascii_letters + string.digits, k=16)
    )


@router.post("", response_model=OrderResponse, status_code=201)
def create_public_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
):
    if data.amount < 100:
        raise HTTPException(
            status_code=400,
            detail="amount must be at least 100",
        )

    merchant = (
        db.query(Merchant)
        .filter(Merchant.id == data.merchant_id)
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Merchant not found",
        )

    order = Order(
        id=generate_order_id(),
        merchant_id=merchant.id,
        amount=data.amount,
        currency=data.currency,
        receipt=data.receipt,
        notes=data.notes,
        status="created",
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order

@router.get("/{order_id}", response_model=OrderResponse)
def get_public_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return not_found("Order not found")
    return order