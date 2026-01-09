# utils/settings.py
import os

TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

TEST_PAYMENT_SUCCESS = (
    os.getenv("TEST_PAYMENT_SUCCESS", "true").lower() == "true"
)

TEST_PROCESSING_DELAY = int(
    os.getenv("TEST_PROCESSING_DELAY", "1000")
)

# success rates (used when NOT in test mode)
UPI_SUCCESS_RATE = float(os.getenv("UPI_SUCCESS_RATE", "0.95"))
CARD_SUCCESS_RATE = float(os.getenv("CARD_SUCCESS_RATE", "0.90"))