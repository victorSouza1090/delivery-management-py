from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid
from app.models.base import Base
from app.models.order import OrderStatus

class OrderEvent(Base):
    __tablename__ = "order_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())