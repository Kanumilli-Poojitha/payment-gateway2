from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WebhookLogResponse(BaseModel):
    id: str
    webhook_id: str
    event_type: str
    status: str
    attempts: int
    response_code: Optional[str]
    response_body: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True