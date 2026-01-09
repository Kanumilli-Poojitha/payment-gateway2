from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# -------------------------
# CARD DETAILS (INTERNAL)
# -------------------------
class CardDetails(BaseModel):
    number: str
    expiry_month: int
    expiry_year: int
    cvv: str


# -------------------------
# CARD DETAILS (PUBLIC)
# -------------------------
class PublicCardDetails(BaseModel):
    card_network: str
    card_last4: str


# -------------------------
# PAYMENT CREATE (MERCHANT)
# -------------------------
class PaymentCreate(BaseModel):
    order_id: str
    method: str               # validated in processor
    test_mode: Optional[bool] = None

    # optional – validated later
    vpa: Optional[str] = None
    card: Optional[CardDetails] = None


# -------------------------
# PAYMENT CREATE (PUBLIC)
# -------------------------
class PublicPaymentCreate(BaseModel):
    order_id: str
    method: str
    vpa: Optional[str] = None
    card_network: Optional[str] = None
    card_last4: Optional[str] = None


# -------------------------
# PAYMENT RESPONSE
# -------------------------
class PaymentResponse(BaseModel):
    id: str
    order_id: str
    amount: int
    currency: str
    method: str
    status: str

    vpa: Optional[str] = None
    card_network: Optional[str] = None
    card_last4: Optional[str] = None

    error_code: Optional[str] = None
    error_description: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True