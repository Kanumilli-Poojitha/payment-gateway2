from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    merchant_id = Column(
        String,
        ForeignKey("merchants.id"),
        nullable=False,
        index=True,
    )

    amount = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    receipt = Column(String, nullable=False)
    status = Column(String, nullable=False, default="created")
    notes = Column(JSON, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )