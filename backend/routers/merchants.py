from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Merchant
from utils import generate_id
import secrets

router = APIRouter(
    prefix="/merchants",
    tags=["merchants"]
)

@router.post("", status_code=201)
def create_merchant(db: Session = Depends(get_db)):
    merchant = Merchant(
        id=generate_id("mrc_"),
        email=f"merchant_{secrets.token_hex(4)}@test.com",
        api_key=secrets.token_hex(16),
        api_secret=secrets.token_hex(32),
    )
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    return merchant


@router.get("", status_code=200)
def list_merchants(db: Session = Depends(get_db)):
    return db.query(Merchant).all()