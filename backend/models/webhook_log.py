from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from database import Base
import uuid


class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)

    event = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)

    status = Column(String, default="pending")  # pending | success | failed
    response_code = Column(Integer, nullable=True)
    response_body = Column(String, nullable=True)

    attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("idx_webhook_logs_merchant_id", "merchant_id"),
        Index("idx_webhook_logs_status", "status"),
        Index("idx_webhook_logs_next_retry_at", "next_retry_at"),
    )