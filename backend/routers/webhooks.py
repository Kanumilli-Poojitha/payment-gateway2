from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
import uuid
import secrets
import os

from database import get_db
from models.webhook import Webhook
from models.merchant import Merchant
from auth import authenticate
from utils.errors import bad_request, not_found

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("")
def register_webhook(url: str, merchant=Depends(authenticate), db: Session = Depends(get_db)):
    # If auth failed (returned None) but we are in midpoint, we must fail
    if not merchant:
        raise HTTPException(status_code=401, detail="Authentication required for this operation")

    if not url.startswith("http"):
        return bad_request("Invalid URL")

    webhook = Webhook(
        id=str(uuid.uuid4()),
        merchant_id=merchant.id,
        url=url,
        secret=secrets.token_hex(16)  # HMAC secret
    )
    db.add(webhook)
    db.commit()
    db.refresh(webhook)

    return {"id": webhook.id, "url": webhook.url, "secret": webhook.secret}

@router.get("")
def list_webhooks(
    merchant=Depends(authenticate),
    db: Session = Depends(get_db)
):
    return db.query(Webhook).filter(Webhook.merchant_id == merchant.id, Webhook.active == True).all()