```md
# System Architecture

Components:
- Dashboard (React) – Port 3000
- Checkout Page (React) – Port 3001
- Backend API (FastAPI) – Port 8000
- PostgreSQL Database

Flow:
1. Merchant accesses Dashboard to view API credentials and stats
2. Merchant creates order via API
3. Checkout page fetches order via public API
4. User completes payment
5. Payment is stored and reflected in dashboard

Diagram:

Dashboard ──┐
            │
Checkout ───┼──▶ FastAPI ───▶ PostgreSQL
            │
Swagger ────┘
