import random
import string

def generate_id(prefix: str) -> str:
    chars = string.ascii_letters + string.digits
    return prefix + ''.join(random.choices(chars, k=16))