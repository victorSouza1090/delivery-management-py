from typing import List
from uuid import UUID
from app.db.database import AsyncSessionLocal
from app.models.outbox_event import OutboxEvent
from sqlalchemy import select, update
from app.models.outbox_event import OutboxEvent
from app.repositories.outbox_event_repository_interface import IOutboxEventRepository


class OutboxEventRepository(IOutboxEventRepository):
    async def create(self, session, order_id, event_type, payload):
        outbox = OutboxEvent(
            order_id=order_id,
            event_type=event_type,
            payload=payload,
            sent=False
        )
        session.add(outbox)
        return outbox
        
    async def get_pending_events(self) -> List[OutboxEvent]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(OutboxEvent).where(OutboxEvent.sent == False).order_by(OutboxEvent.created_at)
            )
            return result.scalars().all()

    async def mark_event_sent(self, event_id: UUID) -> None:
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(OutboxEvent).where(OutboxEvent.id == event_id).values(sent=True)
            )
            await session.commit()
