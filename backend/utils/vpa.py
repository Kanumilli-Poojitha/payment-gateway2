# utils/vpa.py
import re

def validate_vpa(vpa: str) -> bool:
    """
    Basic UPI VPA validation: name@bank
    """
    if not vpa:
        return False
    pattern = r"^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$"
    return bool(re.match(pattern, vpa))