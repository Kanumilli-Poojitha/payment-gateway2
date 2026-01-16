from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Request to create refund
class RefundCreate(BaseModel):
    payment_id: str
    amount: int
    reason: Optional[str] = None

# Refund response
class RefundResponse(BaseModel):
    id: str
    payment_id: str
    merchant_id: str
    amount: int
    status: str
    reason: Optional[str]
    error_code: Optional[str]
    error_description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True