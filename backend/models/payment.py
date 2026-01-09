from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)

    order_id = Column(String, ForeignKey("orders.id"), index=True)
    merchant_id = Column(String, ForeignKey("merchants.id"), index=True)

    amount = Column(Integer, nullable=False)
    currency = Column(String, default="INR")

    method = Column(String, nullable=False)   # upi / card
    status = Column(String, nullable=False)   # processing / success / failed

    vpa = Column(String, nullable=True)

    card_network = Column(String, nullable=True)
    card_last4 = Column(String, nullable=True)

    error_code = Column(String, nullable=True)
    error_description = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )