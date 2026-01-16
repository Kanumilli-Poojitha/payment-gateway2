import hmac
import hashlib


def generate_signature(secret: str, body: str) -> str:
    """
    Generate HMAC SHA256 signature from EXACT request body string
    """
    return hmac.new(
        key=secret.encode(),
        msg=body.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()