import asyncio
import logging
from app.dependencies import get_order_repository, get_message_worker
from app.models.order import OrderStatus
from app.repositories.order_repository_interface import IOrderRepository
from app.workers.interfaces import IMessageWorker
from app.core.logging_config import setup_logging

logger = setup_logging(name="worker")

async def handle_event(data, order_repo: IOrderRepository):
    logger.info(f"Recebido evento: {data}")
    payload = data.get("payload", {})
    order_id = payload.get("order_id")
    status = payload.get("status")

    if not order_id or not status:
        logging.warning("Evento sem order_id ou status, ignorado.")
        return

    try:
        current_status = OrderStatus(status)
    except ValueError:
        logger.error(f"Status inválido recebido: {status}")
        return

    next_status = OrderStatus.next(current_status)
    if next_status is None:
        logger.info(f"Status {status} nao possui proximo status, ignorando.")
        return

    await order_repo.update_order_status(order_id, next_status)
    logger.info(f"Order {order_id} atualizada para {next_status} e evento registrado via repository.")

async def main():
    logger.info("Inicializando worker...")
    worker: IMessageWorker = get_message_worker()
    repo: IOrderRepository = get_order_repository()
    async def handler(data):
        await handle_event(data, repo)
    await worker.start(handler)

if __name__ == "__main__":
    asyncio.run(main())