from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random
import string
import uuid

from database import get_db
from models import Order, Merchant
from schemas.order import PublicOrderCreate, OrderResponse

router = APIRouter(
    prefix="/orders/public",
    tags=["public-orders"],
)

# -----------------------------
# Helpers
# -----------------------------
def generate_order_id() -> str:
    return "order_" + "".join(
        random.choices(string.ascii_letters + string.digits, k=16)
    )


def generate_receipt() -> str:
    return "rcpt_" + uuid.uuid4().hex[:12]


# -----------------------------
# CREATE PUBLIC ORDER
# -----------------------------
@router.post("", response_model=OrderResponse, status_code=201)
def create_public_order(
    data: PublicOrderCreate,
    db: Session = Depends(get_db),
):
    if data.amount < 100:
        raise HTTPException(
            status_code=400,
            detail="amount must be at least 100",
        )

    # Public checkout → seeded merchant
    merchant = db.query(Merchant).first()
    if not merchant:
        raise HTTPException(
            status_code=500,
            detail="No merchant configured",
        )

    order = Order(
        id=generate_order_id(),
        merchant_id=merchant.id,
        amount=data.amount,
        currency=data.currency,
        receipt=data.receipt or generate_receipt(),  # ✅ FIX
        notes=data.notes,
        status="created",
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


@router.get("", response_model=list[OrderResponse])
def list_public_orders(db: Session = Depends(get_db)):
    return db.query(Order).limit(10).all()


# -----------------------------
# GET PUBLIC ORDER
# -----------------------------
@router.get("/{order_id}", response_model=OrderResponse)
def get_public_order(
    order_id: str,
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return order