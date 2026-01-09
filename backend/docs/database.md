# Database Schema

## merchants
- id (UUID, PK)
- email (string)
- api_key (string)
- api_secret (string)
- created_at

## orders
- id (UUID, PK)
- merchant_id (FK → merchants.id)
- amount (integer)
- currency (string)
- status (created, paid)
- receipt

## payments
- id (UUID, PK)
- order_id (FK → orders.id)
- method (card, upi)
- amount
- status (success, failed)
- created_at

Relationships:
- One merchant → many orders
- One order → one payment
