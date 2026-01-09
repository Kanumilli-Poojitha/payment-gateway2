from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import merchants, orders, public_orders
from routers import payment, public_payments
from routers import test

# --------------------------------
# APP INIT
# --------------------------------
app = FastAPI(
    title="Payment Gateway API",
    version="1.0.0"
)

# --------------------------------
# CORS (REQUIRED for checkout & dashboard)
# --------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # dashboard
        "http://localhost:3001",  # checkout
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------
# ROUTERS
# --------------------------------
app.include_router(merchants.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(public_orders.router, prefix="/api/v1")
app.include_router(payment.router, prefix="/api/v1")
app.include_router(public_payments.router, prefix="/api/v1")
app.include_router(test.router, prefix="/api/v1")