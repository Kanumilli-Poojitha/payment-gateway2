from fastapi import APIRouter
from datetime import datetime
from database import engine

router = APIRouter()

@router.get("/health")
def health():
    try:
        engine.connect()
        db_status = "connected"
    except:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }