import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.repositories.impl.outbox_event_repository import OutboxEventRepository
from app.models.outbox_event import OutboxEvent
from app.dto.outbox_event_dto import OutboxEventDTO

@pytest.fixture(scope="function")
def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async def create_all():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    import asyncio
    asyncio.get_event_loop().run_until_complete(create_all())
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@pytest.fixture
def repo(session_factory):
    return OutboxEventRepository(
        session_factory=session_factory
    )

@pytest.mark.asyncio
async def test_create_outbox_event(session_factory, repo):
    async with session_factory() as session:
        order_id = str(uuid.uuid4())
        event_type = "OrderCreated"
        payload = {"order_id": order_id, "status": "RECEIVED"}
        dto = await repo.create(session, order_id, event_type, payload)
        assert isinstance(dto, OutboxEventDTO)
        assert dto.order_id == order_id
        assert dto.event_type == event_type
        assert dto.payload["order_id"] == order_id
        assert dto.payload["status"] == "RECEIVED"
        assert dto.sent is False

@pytest.mark.asyncio
async def test_get_pending_events(session_factory, repo):
    async with session_factory() as session:
        order_id = str(uuid.uuid4())
        await repo.create(session, order_id, "OrderCreated", {"order_id": order_id, "status": "RECEIVED"})
        await session.commit()
    events = await repo.get_pending_events()
    assert len(events) == 1
    assert events[0].event_type == "OrderCreated"
    assert events[0].sent is False

@pytest.mark.asyncio
async def test_mark_event_sent(session_factory, repo):
    async with session_factory() as session:
        order_id = str(uuid.uuid4())
        dto = await repo.create(session, order_id, "OrderCreated", {"order_id": order_id, "status": "RECEIVED"})
        await session.commit()
    await repo.mark_event_sent(uuid.UUID(dto.id))
    events = await repo.get_pending_events()
    assert all(e.sent for e in events) or len(events) == 0

@pytest.mark.asyncio
async def test_create_with_string_payload(session_factory, repo):
    async with session_factory() as session:
        order_id = str(uuid.uuid4())
        event_type = "OrderCreated"
        payload = '{"order_id": "%s", "status": "RECEIVED"}' % order_id
        dto = await repo.create(session, order_id, event_type, payload)
        assert isinstance(dto, OutboxEventDTO)
        assert dto.payload["order_id"] == order_id

@pytest.mark.asyncio
async def test_get_pending_events_empty(repo):
    events = await repo.get_pending_events()
    assert events == []