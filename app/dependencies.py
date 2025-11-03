from fastapi import Depends
from app.repositories.impl.order_repository import OrderRepository
from app.repositories.order_repository_interface import IOrderRepository
from app.repositories.impl.outbox_event_repository import OutboxEventRepository
from app.repositories.outbox_event_repository_interface import IOutboxEventRepository
from app.workers.rabbitmq.rabbitmq_worker import RabbitMQWorker
from app.workers.rabbitmq.rabbitmq_publisher import RabbitMQPublisher
from app.workers.interfaces import IMessagePublisher, IMessageWorker

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

def get_message_worker() -> IMessageWorker:
    """
    Retorna a implementação concreta do message worker (RabbitMQ, Kafka, etc.).
    """
    return RabbitMQWorker()

def get_event_publisher() -> IMessagePublisher:
    """
    Retorna a implementação concreta do publicador de eventos.
    """
    return RabbitMQPublisher()