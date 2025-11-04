import pytest

@pytest.mark.asyncio
async def test_create_order(client, db_session):
    customer_name = "João Teste"
    address = "Rua dos Testes, 123"

    response = await client.post("/orders/", json={
        "customer_name": customer_name,
        "address": address
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["customer_name"] == customer_name
    assert data["address"] == address
    assert data["status"] == "RECEIVED"
    assert data["created_at"] is not None
    
@pytest.mark.asyncio
async def test_create_order_with_missing_body(client, db_session):
    response = await client.post("/orders/")
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "validation_error"
    assert "body: Field required" in data["messages"]

@pytest.mark.asyncio
async def test_create_order_with_missing_fields(client, db_session):
    response = await client.post("/orders/", json={})
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "validation_error"
    assert "body.customer_name: Field required" in data["messages"]
    assert "body.address: Field required" in data["messages"]