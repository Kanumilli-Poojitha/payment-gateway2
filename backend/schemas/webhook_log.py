from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WebhookLogResponse(BaseModel):
    id: str
    merchant_id: Optional[str]
    event: Optional[str]
    status: Optional[str]
    attempts: int
    response_code: Optional[int]
    response_body: Optional[str]
    next_retry_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True