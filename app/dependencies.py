from fastapi import Depends
from app.repositories.order_repository import OrderRepository
from app.repositories.order_repository_interface import IOrderRepository
from app.repositories.outbox_event_repository import OutboxEventRepository
from app.repositories.outbox_event_repository_interface import IOutboxEventRepository

def get_order_repository() -> IOrderRepository:
    """
    Retorna a implementação concreta do repositório de pedidos.
    """
    return OrderRepository(get_outbox_event_repository())

def get_outbox_event_repository() -> IOutboxEventRepository:
    """
    Retorna a implementação concreta do repositório de eventos Outbox.
    """
    return OutboxEventRepository()