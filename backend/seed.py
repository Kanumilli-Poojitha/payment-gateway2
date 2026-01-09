from sqlalchemy.orm import Session
from models import Merchant
import uuid

def seed_merchant(db: Session):
    exists = db.query(Merchant).filter_by(email="test@example.com").first()
    if exists:
        return

    merchant = Merchant(
        id=uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
        name="Test Merchant",
        email="test@example.com",
        api_key="key_test_abc123",
        api_secret="secret_test_xyz789"
    )
    db.add(merchant)
    db.commit()