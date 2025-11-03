from sqlalchemy import Column, String, DateTime, Enum, func
import uuid
import enum
from app.models.base import Base

class OrderStatus(str, enum.Enum):
    RECEIVED = "RECEIVED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    
    def next(self):
        sequence = {
            OrderStatus.RECEIVED: OrderStatus.IN_TRANSIT,
            OrderStatus.IN_TRANSIT: OrderStatus.DELIVERED,
            OrderStatus.DELIVERED: None
        }
        return sequence[self]

class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.RECEIVED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())