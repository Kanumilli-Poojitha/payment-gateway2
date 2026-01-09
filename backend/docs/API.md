# Payment Gateway API Documentation

Base URL:
http://localhost:8000/api/v1

---

## Authentication
Merchant APIs require:
- `X-API-KEY`
- `X-API-SECRET`

Public APIs do not require authentication.

---

## Merchants

### GET /merchants/me
Returns merchant details.

Response:
```json
{
  "id": "mrc_xxx",
  "email": "test@example.com"
}

Orders
POST /orders

Creates a merchant order (authenticated).

Request:

{
  "amount": 50000,
  "currency": "INR",
  "receipt": "rcpt_001"
}


Response:

{
  "id": "order_xxx",
  "status": "created"
}

POST /orders/public

Creates a public order for checkout.

Request:

{
  "merchant_id": "mrc_xxx",
  "amount": 50000,
  "currency": "INR",
  "receipt": "rcpt_001"
}

Payments
POST /payments/public

Processes a payment for an order.

Request:

{
  "order_id": "order_xxx",
  "method": "card",
  "test_mode": true,
  "card": {
    "number": "4111111111111111",
    "expiry_month": 12,
    "expiry_year": 2027,
    "cvv": "123"
  }
}


Response:

{
  "id": "pay_xxx",
  "status": "success"
}
