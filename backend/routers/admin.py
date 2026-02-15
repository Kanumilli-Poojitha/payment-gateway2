from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.payment import Payment
from models.reconciliation import PaymentLog
from models import Webhook, WebhookLog
from auth import authenticate
import statistics

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def admin_stats(merchant=Depends(authenticate), db: Session = Depends(get_db)):
    # -------------------------
    # PAYMENTS OVERVIEW
    # -------------------------
    payments_total = db.query(Payment).filter(Payment.merchant_id == merchant.id).count()
    payments_success = db.query(Payment).filter(Payment.merchant_id == merchant.id, Payment.status == "SUCCESS").count()
    payments_failed = db.query(Payment).filter(Payment.merchant_id == merchant.id, Payment.status == "FAILED").count()
    payments_processing = db.query(Payment).filter(Payment.merchant_id == merchant.id, Payment.status == "PROCESSING").count()

    payment_success_rate = (payments_success / payments_total * 100) if payments_total else 0
    payment_failure_rate = (payments_failed / payments_total * 100) if payments_total else 0

    # -------------------------
    # PAYMENT LATENCY
    # -------------------------
    processed_payments = db.query(Payment).filter(
        Payment.merchant_id == merchant.id,
        Payment.status == "SUCCESS"
    ).all()

    latencies = [(p.updated_at - p.created_at).total_seconds() for p in processed_payments]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    p50_latency = statistics.median(latencies) if latencies else 0
    p95_latency = statistics.quantiles(latencies, n=100)[94] if len(latencies) >= 20 else (max(latencies) if latencies else 0)

    # -------------------------
    # WEBHOOKS OVERVIEW
    # -------------------------
    webhooks_total = db.query(WebhookLog).join(Webhook).filter(Webhook.merchant_id == merchant.id).count()
    webhooks_failed = db.query(WebhookLog).join(Webhook).filter(Webhook.merchant_id == merchant.id, WebhookLog.status == "failed").count()
    webhook_retries = db.query(func.sum(WebhookLog.attempts)).join(Webhook).filter(Webhook.merchant_id == merchant.id).scalar() or 0
    webhook_success_rate = ((webhooks_total - webhooks_failed) / webhooks_total * 100) if webhooks_total else 0

    # -------------------------
    # RETURN FULL STATS
    # -------------------------
    return {
        "payments": {
            "total": payments_total,
            "success": payments_success,
            "failed": payments_failed,
            "processing": payments_processing,
            "success_rate_pct": round(payment_success_rate, 2),
            "failure_rate_pct": round(payment_failure_rate, 2),
        },
        "webhooks": {
            "total": webhooks_total,
            "failed": webhooks_failed,
            "retries": webhook_retries,
            "success_rate_pct": round(webhook_success_rate, 2),
        },
        "latency_sec": {
            "avg": round(avg_latency, 3),
            "min": round(min_latency, 3),
            "max": round(max_latency, 3),
            "p50": round(p50_latency, 3),
            "p95": round(p95_latency, 3),
        }
    }