import re
from datetime import datetime

def validate_vpa(vpa: str) -> bool:
    pattern = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$"
    return bool(re.fullmatch(pattern, vpa))

def luhn_check(card_number: str) -> bool:
    num = card_number.replace(" ", "").replace("-", "")
    if not num.isdigit() or not 13 <= len(num) <= 19:
        return False
    total = 0
    reverse_digits = num[::-1]
    for i, d in enumerate(reverse_digits):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

def detect_card_network(card_number: str) -> str:
    n = card_number.replace(" ", "").replace("-", "")
    if n.startswith("4"):
        return "visa"
    elif n[:2] in ["51","52","53","54","55"]:
        return "mastercard"
    elif n[:2] in ["34","37"]:
        return "amex"
    elif n[:2] in ["60","65"] or n[:2] in [str(i) for i in range(81,90)]:
        return "rupay"
    return "unknown"

def validate_expiry(month: str, year: str) -> bool:
    try:
        m = int(month)
        y = int(year)
        if y < 100:  # 2-digit year
            y += 2000
        if not 1 <= m <= 12:
            return False
        now = datetime.now()
        return (y, m) >= (now.year, now.month)
    except:
        return False