from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Index
from sqlalchemy.sql import func
from database import Base

class Refund(Base):
    __tablename__ = "refunds"

    id = Column(String, primary_key=True, index=True)
    payment_id = Column(String, ForeignKey("payments.id"), nullable=False)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)

    amount = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending | processed

    reason = Column(String, nullable=True)
    error_code = Column(String, nullable=True)
    error_description = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_refunds_payment_id", "payment_id"),
    )