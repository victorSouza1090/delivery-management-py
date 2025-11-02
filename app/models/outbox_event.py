import uuid
from sqlalchemy import Column, String, Boolean, JSON, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.database import Base

class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(PG_UUID(as_uuid=True), nullable=False)
    event_type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)
    sent = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())