
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime
from app.services.order_service import OrderService
from app.repositories.order_repository_interface import IOrderRepository
from app.models.order import Order, OrderStatus
from app.models.order_event import OrderEvent
from app.schemas.order_schema import OrderCreate
from app.core.exceptions.orders.orderNotFoundError import OrderNotFoundError

@pytest.fixture
def mock_repo():
    return AsyncMock(spec=IOrderRepository)

@pytest.mark.asyncio
async def test_create_order_success(mock_repo):
    mock_order = Order(id=uuid4(), customer_name="João", address="Rua X", status=OrderStatus.RECEIVED, created_at=datetime.now())
    mock_repo.create_order.return_value = mock_order
    service = OrderService(order_repo=mock_repo)
    order_create = OrderCreate(customer_name="João", address="Rua X")
    result = await service.create_order(order_create)
    assert result.customer_name == "João"
    assert result.status == "RECEIVED"
    mock_repo.create_order.assert_awaited_once_with(customer_name="João", address="Rua X")

@pytest.mark.asyncio
async def test_get_order_found(mock_repo):
    mock_order = Order(id=uuid4(), customer_name="João", address="Rua X", status=OrderStatus.RECEIVED, created_at=datetime.now())
    mock_repo.get_order_by_id.return_value = mock_order
    service = OrderService(order_repo=mock_repo)
    result = await service.get_order(mock_order.id)
    assert result.id == str(mock_order.id)
    assert result.status == "RECEIVED"
    mock_repo.get_order_by_id.assert_awaited_once_with(mock_order.id)

@pytest.mark.asyncio
async def test_get_order_not_found(mock_repo):
    mock_repo.get_order_by_id.return_value = None
    service = OrderService(order_repo=mock_repo)
    with pytest.raises(OrderNotFoundError):
        await service.get_order(uuid4())
    mock_repo.get_order_by_id.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_order_events(mock_repo):
    order_id = uuid4()
    mock_events = [
        OrderEvent(id=uuid4(), order_id=order_id, status=OrderStatus.RECEIVED, timestamp=datetime(2025, 11, 1, 20, 0, 0)),
        OrderEvent(id=uuid4(), order_id=order_id, status=OrderStatus.IN_TRANSIT, timestamp=datetime(2025, 11, 1, 20, 5, 0)),
        OrderEvent(id=uuid4(), order_id=order_id, status=OrderStatus.DELIVERED, timestamp=datetime(2025, 11, 1, 20, 30, 0)),
    ]
    mock_repo.get_order_events.return_value = mock_events
    service = OrderService(order_repo=mock_repo)
    events = await service.get_order_events(order_id)
    assert len(events) == 3
    assert events[0].status == "RECEIVED"
    assert events[1].status == "IN_TRANSIT"
    assert events[2].status == "DELIVERED"
    for event in events:
        assert event.order_id == str(order_id)
    mock_repo.get_order_events.assert_awaited_once_with(order_id)
