import asyncio
import json
import logging
from aio_pika import connect_robust, IncomingMessage, ExchangeType
from app.core.config import settings
from app.dependencies import get_order_repository
from app.models.order import OrderStatus
from app.repositories.order_repository_interface import IOrderRepository

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

async def handle_message(message: IncomingMessage):
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            logging.info(f"Recebido evento: {data}")
            order_id = data.get("order_id")
            status = data.get("status")

            if not order_id or not status:
                logging.warning("Evento sem order_id ou status, ignorado.")
                return

            try:
                current_status = OrderStatus(status)
            except ValueError:
                logging.error(f"Status inválido recebido: {status}")
                raise

            next_status = OrderStatus.next(current_status)
            if next_status is None:
                logging.info(f"Status {status} não possui próximo status, ignorando.")
                return

            repo: IOrderRepository = get_order_repository()
            await repo.update_order_status(order_id, next_status)
            logging.info(f"Order {order_id} atualizada para {next_status} e evento registrado via repository.")
        except Exception as e:
            logging.error(f"Erro ao processar mensagem: {e}")
            raise

async def main():
    logging.info("Inicializando worker e conectando ao RabbitMQ...")
    connection = await connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()

    exchange = await channel.declare_exchange("delivery_events", ExchangeType.FANOUT)
    queue = await channel.declare_queue("delivery_worker_queue", durable=True)
    await queue.bind(exchange)

    logging.info("Worker aguardando eventos...")
    await queue.consume(handle_message)

    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())