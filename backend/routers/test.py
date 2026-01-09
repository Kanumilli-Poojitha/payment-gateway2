from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.merchant import Merchant

router = APIRouter(prefix="/test", tags=["test"])



@router.get("/merchant")
def test_merchant(db: Session = Depends(get_db)):
    merchant = db.query(Merchant).first()

    return {
        "id": merchant.id,
        "email": merchant.email,
        "api_key": merchant.api_key,
        "api_secret": merchant.api_secret,
        "seeded": True,
    }
