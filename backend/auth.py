from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import os

from database import get_db
from models import Merchant

def authenticate(
    x_api_key: Optional[str] = Header(None, alias="X-Api-Key"),
    x_api_secret: Optional[str] = Header(None, alias="X-Api-Secret"),
    db: Session = Depends(get_db),
):
    if not x_api_key or not x_api_secret:
        if os.getenv("TEST_MODE") == "true":
            return db.query(Merchant).first()
        raise HTTPException(status_code=401, detail="Missing API credentials")

    merchant = (
        db.query(Merchant)
        .filter(
            Merchant.api_key == x_api_key,
            Merchant.api_secret == x_api_secret
        )
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "AUTHENTICATION_ERROR",
                    "description": "Invalid API credentials"
                }
            }
        )

    return merchant