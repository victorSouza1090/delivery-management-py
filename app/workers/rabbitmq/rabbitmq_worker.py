import asyncio
import json
from aio_pika import connect_robust, ExchangeType
from app.core.config import settings
from app.workers.interfaces import IMessageWorker
from app.core.logging_config import setup_logging

logger = setup_logging(name="rabbitmq_worker")

class RabbitMQWorker(IMessageWorker):
    async def setup_dead_letter(self, channel):
        dlx = await channel.declare_exchange("delivery_events_dlx", ExchangeType.FANOUT)
        dlq = await channel.declare_queue("delivery_worker_dlq", durable=True)
        await dlq.bind(dlx)
        return dlx, dlq

    async def setup_main_queue(self, channel, dlx_name):
        args = {
            "x-dead-letter-exchange": dlx_name
        }
        exchange = await channel.declare_exchange("delivery_events", ExchangeType.FANOUT)
        queue = await channel.declare_queue("delivery_worker_queue", durable=True, arguments=args)
        await queue.bind(exchange)
        return exchange, queue

    async def start(self, handler):
        import logging
        connection = await connect_robust(settings.rabbitmq_url)
        logger.info("[RabbitMQWorker] Conectado ao RabbitMQ")
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        dlx, _ = await self.setup_dead_letter(channel)
        _, queue = await self.setup_main_queue(channel, dlx.name)

        async def on_message(message):
            try:
                logger.info(f"[RabbitMQWorker] Mensagem recebida: {message.body}")
                data = json.loads(message.body.decode())
                await handler(data)
                await message.ack()
                logger.info("[RabbitMQWorker] Mensagem processada e ack enviada")
            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {e}. A mensagem será enviada para a DLQ.")
                await message.reject(requeue=False)

        await queue.consume(on_message)
        logger.info("[RabbitMQWorker] Consumidor iniciado, aguardando mensagens...")
        await asyncio.Future()
