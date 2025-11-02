from pydantic import BaseModel
from datetime import datetime

class OrderCreate(BaseModel):
    customer_name: str
    address: str

class OrderResponse(BaseModel):
    id: str
    customer_name: str
    address: str
    status: str
    created_at: datetime

class OrderEventResponse(BaseModel):
    id: str
    order_id: str
    status: str
    timestamp: datetime