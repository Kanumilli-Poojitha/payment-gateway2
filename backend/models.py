from sqlalchemy import (
    Column, String, Integer, ForeignKey,
    DateTime, JSON, Index, Boolean
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
    refunds = relationship("Refund", back_populates="merchant")
    webhooks = relationship("Webhook", back_populates="merchant")


# =======================
# Order
# =======================
class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)

    amount = Column(Integer, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="created")  # created → paid / failed

    receipt = Column(String)
    notes = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

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

    status = Column(String, default="processing")  # processing → success / failed

    vpa = Column(String)
    card_network = Column(String)
    card_last4 = Column(String)

    error_code = Column(String)
    error_description = Column(String)

    idempotency_key = Column(String, unique=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    order = relationship("Order", back_populates="payments")
    merchant = relationship("Merchant", back_populates="payments")
    refunds = relationship("Refund", back_populates="payment")


# =======================
# Refund
# =======================
class Refund(Base):
    __tablename__ = "refunds"

    id = Column(String, primary_key=True)
    payment_id = Column(String, ForeignKey("payments.id"), nullable=False)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)

    amount = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending → processed / failed

    reason = Column(String)
    error_code = Column(String)
    error_description = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    payment = relationship("Payment", back_populates="refunds")
    merchant = relationship("Merchant", back_populates="refunds")


# =======================
# Webhook Subscription
# =======================
class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(String, primary_key=True)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)

    url = Column(String, nullable=False)
    secret = Column(String, nullable=False)
    active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    merchant = relationship("Merchant", back_populates="webhooks")
    logs = relationship("WebhookLog", back_populates="webhook")


# =======================
# Webhook Logs (CRITICAL)
# =======================
class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    id = Column(String, primary_key=True)
    webhook_id = Column(String, ForeignKey("webhooks.id"))

    event_type = Column(String)
    payload = Column(JSON)

    status = Column(String, default="pending")
    attempts = Column(Integer, default=0)
    response_code = Column(String)
    response_body = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    webhook = relationship("Webhook", back_populates="logs")


# =======================
# Indexes
# =======================
Index("idx_orders_merchant", Order.merchant_id)
Index("idx_payments_order", Payment.order_id)
Index("idx_payments_status", Payment.status)
Index("idx_refunds_status", Refund.status)
Index("idx_webhook_logs_status", WebhookLog.status)