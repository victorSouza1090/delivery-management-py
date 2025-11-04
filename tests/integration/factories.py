import uuid
from app.repositories.impl.order_repository import OrderRepository
from app.repositories.impl.outbox_event_repository import OutboxEventRepository

async def create_order_factory(customer_name: str, address: str, session):
    outbox_repo = OutboxEventRepository(lambda: session)
    repo = OrderRepository(outbox_repo, lambda: session)
    return await repo.create_order(customer_name=customer_name, address=address)


async def create_outbox_event_factory(order_id=None, event_type="OrderCreated", payload=None, sent=False, session=None):
    order_id = order_id or str(uuid.uuid4())
    outbox_repo = OutboxEventRepository(lambda: session)
    event_dto = await outbox_repo.create(session, order_id, event_type, payload or {"test": "test"})
    if sent:
        await outbox_repo.mark_event_sent(event_dto.id)
    return event_dto

async def update_order_status_factory(order_id, new_status, session):
    outbox_repo = OutboxEventRepository(lambda: session)
    repo = OrderRepository(outbox_repo, lambda: session)
    await repo.update_order_status(order_id, new_status)
