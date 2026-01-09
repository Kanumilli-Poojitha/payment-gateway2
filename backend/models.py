from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


# =======================
# Merchant
# =======================
class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    api_secret = Column(String, nullable=False)

    orders = relationship("Order", back_populates="merchant")
    payments = relationship("Payment", back_populates="merchant")


# =======================
# Order
# =======================
class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)

    amount = Column(Integer, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="created")

    receipt = Column(String, nullable=True)
    notes = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    merchant = relationship("Merchant", back_populates="orders")
    payments = relationship("Payment", back_populates="order")


# =======================
# Payment
# =======================
class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)

    amount = Column(Integer, nullable=False)
    currency = Column(String, default="INR")
    method = Column(String, nullable=False)
    status = Column(String, default="processing")

    # payment details
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

    order = relationship("Order", back_populates="payments")
    merchant = relationship("Merchant", back_populates="payments")


# =======================
# Indexes (performance)
# =======================
Index("idx_orders_merchant_id", Order.merchant_id)
Index("idx_payments_order_id", Payment.order_id)
Index("idx_payments_status", Payment.status)