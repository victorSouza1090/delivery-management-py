import asyncio
import json
import logging
from aio_pika import connect_robust, ExchangeType
from app.core.config import settings
from app.workers.interfaces import IMessageWorker

class RabbitMQWorker(IMessageWorker):
    async def start(self, handler):
        connection = await connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        exchange = await channel.declare_exchange("delivery_events", ExchangeType.FANOUT)
        queue = await channel.declare_queue("delivery_worker_queue", durable=True)
        await queue.bind(exchange)

        async def on_message(message):
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                    await handler(data)
                except Exception as e:
                    logging.error(f"Erro ao processar mensagem: {e}")

        await queue.consume(on_message)
        await asyncio.Future()
