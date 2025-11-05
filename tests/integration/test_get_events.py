import pytest
import uuid
from tests.integration.factories import create_order_factory, update_order_status_factory
from app.models.order import OrderStatus

@pytest.mark.asyncio
async def test_get_order_events_by_order_id(client, db_session):
    # Cria uma ordem usando a factory
    customer_name = "João Teste"
    address = "Rua dos Testes, 123"
    order = await create_order_factory(customer_name, address, db_session)
    order_id = order.id if hasattr(order, "id") else order["id"]

    # Atualiza status da ordem
    await update_order_status_factory(order_id, OrderStatus.IN_TRANSIT, db_session)
    await update_order_status_factory(order_id, OrderStatus.DELIVERED, db_session)

    response = await client.get(f"/orders/{order_id}/events")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 3 
    for event, expected_status in zip(data, ["RECEIVED", "IN_TRANSIT", "DELIVERED"]):
        assert "id" in event
        assert event["order_id"] == order_id
        assert event["status"] == expected_status
        assert "timestamp" in event

@pytest.mark.asyncio
async def test_get_order_events_by_order_id_not_found(client):
    non_existent_order_id = uuid.uuid4()
    response = await client.get(f"/orders/{non_existent_order_id}/events")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "order_not_found"
    assert data["detail"] == f"Order {non_existent_order_id} not found"

@pytest.mark.asyncio
async def test_get_order_events_by_order_id_invalid(client):
    invalid_order_id = 99999
    response = await client.get(f"/orders/{invalid_order_id}/events")
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "validation_error"
    assert data["messages"] == ["path.order_id: Invalid UUID format"]
