import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PORT = int(os.getenv("PORT", 8000))

TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
TEST_PAYMENT_SUCCESS = os.getenv("TEST_PAYMENT_SUCCESS", "true").lower() == "true"
TEST_PROCESSING_DELAY = int(os.getenv("TEST_PROCESSING_DELAY", "1000"))

UPI_SUCCESS_RATE = float(os.getenv("UPI_SUCCESS_RATE", "0.9"))
CARD_SUCCESS_RATE = float(os.getenv("CARD_SUCCESS_RATE", "0.95"))

TEST_MERCHANT_EMAIL = os.getenv("TEST_MERCHANT_EMAIL")
TEST_API_KEY = os.getenv("TEST_API_KEY")
TEST_API_SECRET = os.getenv("TEST_API_SECRET")
