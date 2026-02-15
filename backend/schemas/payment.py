from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CardDetails(BaseModel):
    number: str
    expiry_month: int
    expiry_year: int
    cvv: str


class PaymentCreate(BaseModel):
    order_id: str
    method: str
    vpa: Optional[str] = None
    card: Optional[CardDetails] = None


class CaptureRequest(BaseModel):
    amount: Optional[int] = None


class PaymentResponse(BaseModel):
    id: str
    order_id: str
    merchant_id: Optional[str]
    amount: int
    currency: Optional[str]
    method: str
    status: str
    captured: bool
    error_code: Optional[str]
    error_description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True