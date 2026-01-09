from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

# =========================
# PUBLIC ORDER SCHEMA
# =========================
class PublicOrderCreate(BaseModel):
    amount: int
    currency: str = "INR"
    receipt: Optional[str] = None
    notes: Optional[Dict[str, str]] = None


# =========================
# MERCHANT ORDER SCHEMA
# =========================
class OrderCreate(BaseModel):
    merchant_id: str
    amount: int
    currency: str = "INR"
    receipt: Optional[str] = None
    notes: Optional[Dict[str, str]] = None


# =========================
# RESPONSE SCHEMA
# =========================
class OrderResponse(BaseModel):
    id: str
    merchant_id: str
    amount: int
    currency: str
    status: str
    receipt: Optional[str]
    notes: Optional[Dict[str, str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True