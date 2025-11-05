import json
from aio_pika import connect_robust, ExchangeType, Message
from app.core.config import settings
from app.workers.interfaces import IMessagePublisher
from app.core.logging_config import setup_logging

logger = setup_logging(name="rabbitmq_publisher")


class RabbitMQPublisher(IMessagePublisher):
    async def publish(self, event: dict):
        connection = await connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()
        exchange = await channel.declare_exchange("delivery_events", ExchangeType.FANOUT)
        body = json.dumps(event).encode()
        logger.info(f"[RabbitMQPublisher] Publicando mensagem: {event}")
        await exchange.publish(
            Message(body=body),
            routing_key=""
        )
        logger.info("[RabbitMQPublisher] Mensagem publicada com sucesso")
        await connection.close()
