import pytest
import asyncio
from app.dependencies import get_event_publisher, get_outbox_event_repository
from tests.integration.factories import update_order_status_factory
from app.models.order import OrderStatus
from app.repositories.impl.order_repository import OrderRepository
from app.workers.worker import main


@pytest.mark.asyncio
async def test_worker_process_event(db_session, order_factory):
    # Cria um pedido
    order = await order_factory(customer_name="Teste Worker", address="Rua Teste")
    repo = OrderRepository(get_outbox_event_repository(), lambda: db_session)

    #publicação de evento na fila
    publisher = get_event_publisher()
    await publisher.publish({
        "order_id": str(order.id),
        "event_type": "OrderCreated",
        "payload": {
                "order_id": str(order.id),
                "status": "RECEIVED"
        }
    })

    # Inicia o worker para consumir o evento
    task = asyncio.create_task(main())
    await asyncio.sleep(3)  # tempo para o worker consumir/processar
    task.cancel()

    # Verifica se o status foi atualizado
    updated_order = await repo.get_order_by_id(order.id)
    assert updated_order.status == OrderStatus.IN_TRANSIT

    # Verifica se o evento foi registrado
    events = await repo.get_order_events(order.id)
    assert any(e.status == OrderStatus.IN_TRANSIT for e in events)

@pytest.mark.asyncio
async def test_worker_process_event_should_not_update(db_session, order_factory):
    # Cria um pedido
    order = await order_factory(customer_name="Teste Worker", address="Rua Teste")
    await update_order_status_factory(order.id, OrderStatus.IN_TRANSIT, db_session)
    await update_order_status_factory(order.id, OrderStatus.DELIVERED, db_session)
    repo = OrderRepository(get_outbox_event_repository(), lambda: db_session)

    #publicação de evento na fila
    publisher = get_event_publisher()
    await publisher.publish({
        "order_id": str(order.id),
        "event_type": "OrderCreated",
        "payload": {
                "order_id": str(order.id),
                "status": "DELIVERED"
        }
    })

    # Inicia o worker para consumir o evento
    task = asyncio.create_task(main())
    await asyncio.sleep(3)  # tempo para o worker consumir/processar
    task.cancel()

    # Verifica se o status foi permanece o mesmo
    updated_order = await repo.get_order_by_id(order.id)
    assert updated_order.status == OrderStatus.DELIVERED

    # Verifica se a quantidade permanece a mesma
    events = await repo.get_order_events(order.id)
    assert isinstance(events, list)
    assert len(events) == 3
    
@pytest.mark.asyncio
async def test_worker_process_event_invalid_Status(db_session, order_factory):
    # Cria um pedido
    order = await order_factory(customer_name="Teste Worker", address="Rua Teste")
    repo = OrderRepository(get_outbox_event_repository(), lambda: db_session)
    #publicação de evento na fila
    publisher = get_event_publisher()
    await publisher.publish({
        "order_id": str(order.id),
        "event_type": "OrderCreated",
        "payload": {
                "order_id": str(order.id),
                "status": "TesteInvalid"
        }
    })

    # Inicia o worker para consumir o evento
    task = asyncio.create_task(main())
    await asyncio.sleep(3)  # tempo para o worker consumir/processar
    task.cancel()

    # Verifica se o status foi permanece o mesmo
    updated_order = await repo.get_order_by_id(order.id)
    assert updated_order.status == OrderStatus.RECEIVED

    # Verifica se a quantidade permanece a mesma
    events = await repo.get_order_events(order.id)
    assert isinstance(events, list)
    assert len(events) == 1