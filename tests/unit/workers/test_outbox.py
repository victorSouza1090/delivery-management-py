import pytest
from unittest.mock import AsyncMock
from app.workers import outbox
from app.dto.outbox_event_dto import OutboxEventDTO

@pytest.mark.asyncio
async def test_publish_event_success():
    publisher = AsyncMock()
    event = OutboxEventDTO(
        id="evt-1",
        order_id="123",
        event_type="OrderCreated",
        payload={"order_id": "123", "status": "RECEIVED"},
        sent=False,
        created_at=None
    )
    await outbox.publish_event(event, publisher)
    publisher.publish.assert_awaited_once()

@pytest.mark.asyncio
async def test_publish_event_error():
    publisher = AsyncMock()
    publisher.publish.side_effect = Exception("Falha")
    event = OutboxEventDTO(
        id="evt-2",
        order_id="456",
        event_type="OrderCreated",
        payload={"order_id": "456", "status": "RECEIVED"},
        sent=False,
        created_at=None
    )
    with pytest.raises(Exception):
        await outbox.publish_event(event, publisher)

@pytest.mark.asyncio
async def test_process_outbox():
    publisher = AsyncMock()
    repo = AsyncMock()
    # Dois eventos pendentes
    event1 = OutboxEventDTO(id="evt-1", order_id="123", event_type="OrderCreated", payload={}, sent=False, created_at=None)
    event2 = OutboxEventDTO(id="evt-2", order_id="456", event_type="OrderCreated", payload={}, sent=False, created_at=None)
    repo.get_pending_events = AsyncMock(side_effect=[[event1, event2], []])
    repo.mark_event_sent = AsyncMock()
    # Executa um ciclo do loop
    try:
        await outbox.process_outbox(repo, publisher)
    except StopAsyncIteration:
        pass  # Ignora o erro de fim de mock
    publisher.publish.assert_awaited()
    repo.mark_event_sent.assert_awaited()