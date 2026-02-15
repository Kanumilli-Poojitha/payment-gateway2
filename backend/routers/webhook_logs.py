from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json
import redis
import os

from database import get_db
from auth import authenticate
from models.webhook_log import WebhookLog
from schemas.webhook_log import WebhookLogResponse
from utils.errors import not_found

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
QUEUE_NAME = os.getenv("WEBHOOK_QUEUE", "gateway_webhooks")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

router = APIRouter(prefix="/webhook-logs", tags=["webhook-logs"])


# -------------------------------------------------
# GET webhook delivery logs (merchant dashboard)
# -------------------------------------------------
@router.get("", response_model=list[WebhookLogResponse])
def list_webhook_logs(
    merchant=Depends(authenticate),
    db: Session = Depends(get_db),
):

    return (
        db.query(WebhookLog)
        .filter(WebhookLog.merchant_id == merchant.id)
        .order_by(WebhookLog.created_at.desc())
        .all()
    )


# -------------------------------------------------
# POST retry failed webhook
# -------------------------------------------------
@router.post("/{log_id}/retry")
def retry_webhook(
    log_id: str,
    merchant=Depends(authenticate),
    db: Session = Depends(get_db),
):
    log = (
        db.query(WebhookLog)
        .filter(
            WebhookLog.id == log_id,
            WebhookLog.merchant_id == merchant.id,
        )
        .first()
    )

    if not log:
        not_found("Webhook log not found")

    # Re-enqueue. 
    # Since we have a retry thread in WebhookWorker that polls 'pending',
    # we just need to reset the status and next_retry_at.
    from datetime import datetime
    log.status = "pending"
    log.next_retry_at = datetime.utcnow()
    log.attempts = 0 # Reset attempts for a fresh 5-try cycle or just one?
    # Requirement: "Manual Retry - Re-enqueue webhook delivery job"
    
    db.commit()

    return {"message": "Webhook retry scheduled"}