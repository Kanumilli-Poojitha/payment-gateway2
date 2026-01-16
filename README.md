Build Production-Ready Payment Gateway with Async Processing and Webhooks

A fully containerized, production-inspired payment gateway system inspired by Razorpay/Stripe.
Supports merchant onboarding, order management, UPI & Card payments, async processing, refunds,
webhook delivery with retries & HMAC verification, and an embeddable JavaScript SDK.

Built to demonstrate real-world fintech architecture: async workers, job queues, idempotency,
webhook reliability, and end-to-end payment flows.

------------------------------------------------------------

🚀 Features

• Merchant authentication using API Key & Secret
• Public & merchant order APIs
• Multi-method payments:
  - UPI (VPA validation)
  - Card payments (network detection, masking)
• Deterministic test mode for automated evaluation
• Async payment processing via Redis queues
• Refund system with async worker
• Webhook delivery system:
  - Event-based (payment.success / payment.failed / refund.processed)
  - HMAC SHA256 signatures
  - Retry mechanism with DLQ
• Embeddable JavaScript Checkout SDK
• Hosted Checkout Page
• Merchant Dashboard
• Fully Dockerized (single command startup)

------------------------------------------------------------

🏗️ System Architecture

Dashboard (3000)
   │
   │ Auth APIs
   ▼
FastAPI Gateway (8000)
   │
   ├── Orders
   ├── Payments
   ├── Refunds
   ├── Webhooks
   ├── Public APIs
   │
   ▼
PostgreSQL (5432)

Async Workers:
• Payment Worker
• Refund Worker
• Webhook Worker

Redis (6379)
• Payment queue
• Webhook queue
• Dead-letter queue

Checkout Page (3001)
Embeddable SDK (gateway.js)

------------------------------------------------------------

📁 Project Structure

payment-gateway/
├── docker-compose.yml
├── README.md
├── submission.yml
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── models/
│   │   ├── workers/
│   │   ├── utils/
├── frontend/
│   ├── sdk/
│   │   └── gateway.js
│   └── dashboard/
├── checkout-page/

------------------------------------------------------------

🐳 Docker Setup

Start all services:

docker-compose up -d

Ports:

| Service          | Port |
|------------------|------|
| API              | 8000 |
| Dashboard        | 3000 |
| Checkout Page    | 3001 |
| Redis            | 6379 |
| PostgreSQL       | 5432 |                             |

All services start automatically with correct dependency ordering.

------------------------------------------------------------

🔐 Test Merchant (Auto-Seeded)

| Field        | Value |
|-------------|-------|
| Merchant ID | test_merchant |
| API Key     | key_test_abc123 |
| API Secret  | secret_test_xyz789 |

------------------------------------------------------------

📦 API Overview

Health  
GET /health

Orders (Merchant)  
POST /api/v1/orders  
GET /api/v1/orders/{order_id}

Payments (Merchant)  
POST /api/v1/payments  
GET /api/v1/payments/{payment_id}

Public APIs (No Auth)  
POST /api/v1/orders/public  
GET /api/v1/orders/public/{order_id}  
POST /api/v1/payments/public  
GET /api/v1/payments/public/{payment_id}

Refunds  
POST /api/v1/refunds  
GET /api/v1/refunds/{refund_id}

------------------------------------------------------------

Create Payment (Public / SDK)

POST /api/v1/payments/public
Headers:
Idempotency-Key (optional)

UPI:
{
  "order_id": "order_22hJz371jXdn3yaw",
  "amount": 50000,
  "currency": "INR",
  "method": "upi",
  "vpa": "user@upi"
}

Card:
{
  "order_id": "order_22hJz371jXdn3yaw",
  "amount": 50000,
  "currency": "INR",
  "method": "card",
  "card": {
    "number": "4111111111111111",
    "expiry_month": 12,
    "expiry_year": 2030,
    "cvv": "123"
  }
}

Response:
{
  "id": "pay_XXXX",
  "order_id": "order_22hJz371jXdn3yaw",
  "merchant_id": "mrc_XXXX",
  "amount": 50000,
  "currency": "INR",
  "method": "upi",
  "status": "CREATED",
  "captured": false,
  "error_code": null,
  "error_description": null,
  "created_at": "2026-01-16T05:08:17.841529Z",
  "updated_at": null
}

Payment Capture
POST /api/v1/payments/{payment_id}/capture
Headers:
Idempotency-Key (optional)

Response:
{
  "id": "pay_XXXX",
  "order_id": "order_22hJz371jXdn3yaw",
  "merchant_id": "mrc_XXXX",
  "amount": 50000,
  "currency": "INR",
  "method": "upi",
  "status": "SUCCESS",
  "captured": true,
  "error_code": null,
  "error_description": null,
  "created_at": "2026-01-16T05:08:17.841529Z",
  "updated_at": "2026-01-16T05:10:00.123456Z"
}
------------------------------------------------------------
🧪 Evaluator Test Endpoints

Enqueue Test Job:
POST /api/v1/test/jobs/enqueue

Check Job Queue Status:
GET /api/v1/test/jobs/status

Capture Payment:
POST /api/v1/payments/{payment_id}/capture

Refund Payment:
POST /api/v1/payments/{payment_id}/refunds

------------------------------------------------------------

🔁 Payment State Machine

created → processing → success / failed

Refund State Machine

pending → processed / failed

------------------------------------------------------------

🌐 Webhooks

Events:
• payment.success
• payment.failed
• refund.processed
• refund.failed

Delivery:
• Signed using HMAC SHA256
• Header: X-Signature
• Automatic retries
• DLQ after max retries

------------------------------------------------------------

🧩 Embeddable JavaScript SDK

File:
frontend/sdk/gateway.js

Usage:

<script src="gateway.js"></script>
<script>
  GatewayCheckout.open({
    amount: 50000,
    method: "upi",
    onSuccess: function (payment) {
      console.log("Payment success:", payment.id);
    }
  });
</script>

------------------------------------------------------------

🧪 Test Mode (Evaluator Friendly)

Environment Variables:

TEST_MODE=true  
TEST_PROCESSING_DELAY=500  

Ensures deterministic behavior for automated tests.

------------------------------------------------------------

🖥️ Dashboard (3000)

• Login
• Transaction list
• Payment analytics
• Webhook logs

All required data-test-id attributes implemented.

------------------------------------------------------------

🧾 Hosted Checkout Page (3001)

Flow:
• Fetch order
• Select payment method
• Submit payment
• Poll status
• Show result

------------------------------------------------------------

🗄️ Database Schema

Tables:
• merchants
• orders
• payments
• refunds
• webhooks
• webhook_logs

Indexes on:
• merchant_id
• payment_id
• status fields

Sensitive card data is never stored.

------------------------------------------------------------

🏁 Final Notes

This project demonstrates:
• Async-first payment architecture
• Reliable webhook delivery
• Idempotent APIs
• Real-world system design
• Production-style worker services

video demo:
https://youtu.be/bYjgakEEmzs
