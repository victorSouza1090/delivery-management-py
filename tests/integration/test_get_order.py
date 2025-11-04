import pytest
import uuid
from tests.integration.factories import create_order_factory

@pytest.mark.asyncio
async def test_get_order_by_id(client, db_session):
    # Cria uma ordem usando a factory 
    customer_name = "João Teste"
    address = "Rua dos Testes, 123"
    order = await create_order_factory(customer_name, address, db_session)
    order_id = order.id if hasattr(order, "id") else order["id"]

    response = await client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["customer_name"] == customer_name
    assert data["address"] == address
    assert data["status"] == "RECEIVED"
    assert data["created_at"] is not None

@pytest.mark.asyncio
async def test_get_order_by_id_not_found(client):
    non_existent_order_id = uuid.uuid4()
    response = await client.get(f"/orders/{non_existent_order_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "order_not_found"
    assert data["detail"] == f"Order {non_existent_order_id} not found"

@pytest.mark.asyncio
async def test_get_order_by_id_invalid(client):
    invalid_order_id = 99999
    response = await client.get(f"/orders/{invalid_order_id}")
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "validation_error"
    assert data["messages"] == ["path.order_id: Invalid UUID format"]
