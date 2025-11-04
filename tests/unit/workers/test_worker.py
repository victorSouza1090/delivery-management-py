import pytest
from app.workers.worker import handle_event
from app.models.order import OrderStatus

class DummyRepo:
    def __init__(self):
        self.updated = False
        self.last_id = None
        self.last_status = None
    async def update_order_status(self, order_id, status):
        self.updated = True
        self.last_id = order_id
        self.last_status = status

@pytest.mark.asyncio
async def test_handle_event_valid():
    repo = DummyRepo()
    data = {"payload": {"order_id": "123", "status": "RECEIVED"}}
    await handle_event(data, repo)
    assert repo.updated
    assert repo.last_id == "123"
    assert repo.last_status == OrderStatus.IN_TRANSIT

@pytest.mark.asyncio
async def test_handle_event_missing_fields():
    repo = DummyRepo()
    data = {"payload": {"order_id": None, "status": None}}
    await handle_event(data, repo)
    assert not repo.updated

@pytest.mark.asyncio
async def test_handle_event_invalid_status():
    repo = DummyRepo()
    data = {"payload": {"order_id": "123", "status": "INVALID"}}
    await handle_event(data, repo)
    assert not repo.updated
    
@pytest.mark.asyncio
async def test_handle_event_next_status_none():
    repo = DummyRepo()
    data = {"payload": {"order_id": "123", "status": "DELIVERED"}}
    await handle_event(data, repo)
    assert not repo.updated