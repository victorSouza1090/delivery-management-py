import uuid
from sqlalchemy import Column, String, Boolean, TIMESTAMP, func
from app.models.base import Base
import uuid

class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), nullable=False)
    event_type = Column(String(50), nullable=False)
    payload = Column(String, nullable=False)
    sent = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())