import json
from aio_pika import connect_robust, ExchangeType, Message
from app.core.config import settings
from app.workers.interfaces import IMessagePublisher

class RabbitMQPublisher(IMessagePublisher):
    async def publish(self, event: dict):
        connection = await connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()
        exchange = await channel.declare_exchange("delivery_events", ExchangeType.FANOUT)
        body = json.dumps(event).encode()
        await exchange.publish(
            Message(body=body),
            routing_key=""
        )
        await connection.close()
