from sqlalchemy import Column, String, DateTime, Text, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.sql import func
from database import Base
import uuid


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)

    key = Column(String, nullable=False)

    request_hash = Column(String, nullable=False)
    response = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("merchant_id", "key", name="uq_merchant_idem_key"),
    )