from fastapi import FastAPI
from app.api.routes import orders

app = FastAPI(title="Delivery Service API")

app.include_router(orders.router, prefix="/orders", tags=["Orders"])
