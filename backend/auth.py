from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Merchant

def authenticate(
    x_api_key: str = Header(..., alias="X-Api-Key"),
    x_api_secret: str = Header(..., alias="X-Api-Secret"),
    db: Session = Depends(get_db),
):
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