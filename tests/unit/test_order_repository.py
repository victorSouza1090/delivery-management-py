import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.order import OrderStatus
from app.repositories.impl.order_repository import OrderRepository
from app.repositories.impl.outbox_event_repository import OutboxEventRepository

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
    return OrderRepository(
        outbox_repo=OutboxEventRepository(),
        session_factory=session_factory
    )

@pytest.mark.asyncio
async def test_create_and_get_order(repo):
    order = await repo.create_order("João", "Rua X")
    found = await repo.get_order_by_id(uuid.UUID(order.id))
    assert found is not None
    assert found.id == order.id
    assert found.customer_name == "João"

    events = await repo.get_order_events(uuid.UUID(order.id))
    assert len(events) == 1
    assert events[0].status == OrderStatus.RECEIVED

@pytest.mark.asyncio
async def test_update_order_status(repo):
    order = await repo.create_order("Maria", "Rua Y")
    await repo.update_order_status(uuid.UUID(order.id), OrderStatus.IN_TRANSIT)
    updated = await repo.get_order_by_id(uuid.UUID(order.id))
    assert updated.status == OrderStatus.IN_TRANSIT

@pytest.mark.asyncio
async def test_get_order_events(repo):
    order = await repo.create_order("Carlos", "Rua Z")
    order_id = uuid.UUID(order.id)
    await repo.update_order_status(order_id, OrderStatus.IN_TRANSIT)
    await repo.update_order_status(order_id, OrderStatus.DELIVERED)
    events = await repo.get_order_events(order_id)
    assert len(events) == 3
    assert events[0].status == OrderStatus.RECEIVED
    assert events[1].status == OrderStatus.IN_TRANSIT
    assert events[2].status == OrderStatus.DELIVERED
    
@pytest.mark.asyncio
async def test_update_order_status_no_order(repo):
    fake_id = uuid.uuid4()
    found = await repo.update_order_status(fake_id, OrderStatus.IN_TRANSIT)
    assert found is None

@pytest.mark.asyncio
async def test_update_order_status_same_status(repo):
    order = await repo.create_order("Ana", "Rua W")
    await repo.update_order_status(uuid.UUID(order.id), OrderStatus.RECEIVED)
    updated = await repo.get_order_by_id(uuid.UUID(order.id))
    assert updated.status == OrderStatus.RECEIVED

@pytest.mark.asyncio
async def test_update_order_status_event_exists(repo):
    order = await repo.create_order("Beto", "Rua V")
    order_id = uuid.UUID(order.id)
    await repo.update_order_status(order_id, OrderStatus.IN_TRANSIT)
    # Tenta atualizar para IN_TRANSIT novamente (evento já existe)
    await repo.update_order_status(order_id, OrderStatus.RECEIVED)
    events = await repo.get_order_events(order_id)
    assert len(events) == 2  # Deve ter apenas 2 eventos RECEIVED e IN_TRANSIT

@pytest.mark.asyncio
async def test_get_order_by_id_not_found(repo):
    fake_id = uuid.uuid4()
    found = await repo.get_order_by_id(fake_id)
    assert found is None

@pytest.mark.asyncio
async def test_get_order_events_not_found(repo):
    fake_id = uuid.uuid4()
    events = await repo.get_order_events(fake_id)
    assert events == []