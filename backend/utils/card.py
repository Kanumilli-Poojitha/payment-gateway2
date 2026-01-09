from datetime import datetime

def luhn_check(card_number: str) -> bool:
    num = ''.join(filter(str.isdigit, card_number))
    if not num.isdigit() or not (13 <= len(num) <= 19):
        return False

    total = 0
    reverse = num[::-1]
    for i, d in enumerate(reverse):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def detect_card_network(card_number: str) -> str:
    num = ''.join(filter(str.isdigit, card_number))
    if num.startswith('4'):
        return "visa"
    if num[:2] in ['51','52','53','54','55']:
        return "mastercard"
    if num[:2] in ['34','37']:
        return "amex"
    if num.startswith(('60','65')) or 81 <= int(num[:2]) <= 89:
        return "rupay"
    return "unknown"


def validate_expiry(month: str, year: str) -> bool:
    try:
        month = int(month)
        year = int(year)
        if year < 100:
            year += 2000

        now = datetime.now()
        return (year > now.year) or (year == now.year and month >= now.month)
    except:
        return False