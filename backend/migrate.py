from sqlalchemy import text
from database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration")

def migrate():
    logger.info("Starting database migration...")
    with engine.begin() as conn:
        # 1. Merchants
        logger.info("Checking 'merchants'...")
        conn.execute(text("ALTER TABLE merchants ADD COLUMN IF NOT EXISTS webhook_secret VARCHAR"))
        
        # 2. Refunds
        logger.info("Checking 'refunds'...")
        conn.execute(text("ALTER TABLE refunds ADD COLUMN IF NOT EXISTS merchant_id VARCHAR"))
        conn.execute(text("ALTER TABLE refunds ADD COLUMN IF NOT EXISTS processed_at TIMESTAMP WITH TIME ZONE"))
        
        # 3. WebhookLogs
        logger.info("Checking 'webhook_logs'...")
        conn.execute(text("ALTER TABLE webhook_logs ADD COLUMN IF NOT EXISTS merchant_id VARCHAR"))
        conn.execute(text("ALTER TABLE webhook_logs ADD COLUMN IF NOT EXISTS event VARCHAR"))
        conn.execute(text("ALTER TABLE webhook_logs ADD COLUMN IF NOT EXISTS payload JSON"))
        conn.execute(text("ALTER TABLE webhook_logs ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'pending'"))
        conn.execute(text("ALTER TABLE webhook_logs ADD COLUMN IF NOT EXISTS response_code INTEGER"))
        conn.execute(text("ALTER TABLE webhook_logs ADD COLUMN IF NOT EXISTS response_body VARCHAR"))
        conn.execute(text("ALTER TABLE webhook_logs ADD COLUMN IF NOT EXISTS attempts INTEGER DEFAULT 0"))
        conn.execute(text("ALTER TABLE webhook_logs ADD COLUMN IF NOT EXISTS last_attempt_at TIMESTAMP WITH TIME ZONE"))
        conn.execute(text("ALTER TABLE webhook_logs ADD COLUMN IF NOT EXISTS next_retry_at TIMESTAMP WITH TIME ZONE"))
        
        # 4. Payments
        logger.info("Checking 'payments'...")
        conn.execute(text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS merchant_id VARCHAR"))
        conn.execute(text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS error_code VARCHAR"))
        conn.execute(text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS error_description VARCHAR"))
        conn.execute(text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS processed_at TIMESTAMP WITH TIME ZONE"))
        conn.execute(text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR"))
        conn.execute(text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS captured BOOLEAN DEFAULT FALSE"))
        
        # 5. Orders
        logger.info("Checking 'orders'...")
        conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS currency VARCHAR(3) DEFAULT 'INR'"))
        conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS notes JSON"))

        # 6. Data Cleanup
        logger.info("Linking legacy records to first merchant...")
        result = conn.execute(text("SELECT id FROM merchants LIMIT 1")).fetchone()
        if result:
            first_mrc_id = result[0]
            conn.execute(text("UPDATE orders SET merchant_id = :mrc_id WHERE merchant_id IS NULL"), {"mrc_id": first_mrc_id})
            conn.execute(text("UPDATE webhook_logs SET merchant_id = :mrc_id WHERE merchant_id IS NULL"), {"mrc_id": first_mrc_id})
            conn.execute(text("UPDATE webhook_logs SET event = 'payment.success' WHERE event IS NULL"))
            conn.execute(text("UPDATE webhook_logs SET status = 'success' WHERE status IS NULL"))
            conn.execute(text("UPDATE webhook_logs SET attempts = 0 WHERE attempts IS NULL"))
            conn.execute(text("UPDATE payments SET merchant_id = :mrc_id WHERE merchant_id IS NULL"), {"mrc_id": first_mrc_id})
            conn.execute(text("UPDATE refunds SET merchant_id = :mrc_id WHERE merchant_id IS NULL"), {"mrc_id": first_mrc_id})

    logger.info("Migrations completed successfully.")

if __name__ == "__main__":
    migrate()
