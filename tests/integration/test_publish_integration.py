import pytest
import asyncio
from app.dependencies import get_event_publisher, get_message_worker

@pytest.mark.asyncio
async def test_publisher_sends_message():
    publisher = get_event_publisher()
    event = {
        "order_id": "test-id",
        "event_type": "OrderCreated",
        "payload": {"order_id": "test-id", "status": "RECEIVED"}
    }

    received_events = []

    async def test_handler(data):
        received_events.append(data)

    worker = get_message_worker()
    task = asyncio.create_task(worker.start(test_handler))

    await publisher.publish(event)
    
    async def wait_for_message(received_events):
        while not received_events:
            await asyncio.sleep(0.5)
            
    await asyncio.wait_for(wait_for_message(received_events), timeout=30)

    

    task.cancel()

    assert received_events
    assert received_events[0] == event