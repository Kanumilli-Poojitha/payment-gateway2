from sqlalchemy.orm import Session
from models.merchant import Merchant

TEST_MERCHANT = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "api_key": "key_test_abc123",
    "api_secret": "secret_test_xyz789",
}

def seed_test_merchant(db: Session):
    existing = db.query(Merchant).filter(
        Merchant.api_key == TEST_MERCHANT["api_key"]
    ).first()

    if existing:
        return

    merchant = Merchant(**TEST_MERCHANT)
    db.add(merchant)
    db.commit()