import hashlib
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import IdempotencyKey
import uuid
from fastapi import HTTPException

IDEMPOTENCY_TTL_HOURS = 24


def hash_request(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def get_existing_response(
    db: Session,
    merchant_id: str | None,
    idem_key: str,
    request_payload: dict,
):
    request_hash = hash_request(request_payload)

    record = (
        db.query(IdempotencyKey)
        .filter(
            IdempotencyKey.merchant_id == merchant_id,
            IdempotencyKey.idem_key == idem_key,
            IdempotencyKey.expires_at > datetime.utcnow(),
        )
        .first()
    )

    if not record:
        return None

    # 🚨 SAME KEY + DIFFERENT PAYLOAD = HARD FAIL
    if record.request_hash != request_hash:
        raise HTTPException(
            status_code=409,
            detail="Idempotency key reused with different request payload",
        )

    return {
        "body": json.loads(record.response_body),
        "status_code": int(record.response_code),
    }


def save_idempotency_response(
    db: Session,
    merchant_id: str | None,
    idem_key: str,
    request_payload: dict,
    response_body: dict,
    response_code: int,
):
    record = IdempotencyKey(
        id=str(uuid.uuid4()),
        merchant_id=merchant_id,
        idem_key=idem_key,
        request_hash=hash_request(request_payload),
        response_body=json.dumps(response_body, default=str),
        response_code=str(response_code),
        expires_at=datetime.utcnow() + timedelta(hours=IDEMPOTENCY_TTL_HOURS),
    )

    db.add(record)
    db.commit()