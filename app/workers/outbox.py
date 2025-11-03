import asyncio
import logging
from app.dto.outbox_event_dto import OutboxEventDTO
from app.dependencies import get_event_publisher, get_outbox_event_repository
from app.repositories.outbox_event_repository_interface import IOutboxEventRepository
from app.workers.interfaces import IMessagePublisher
from app.core.logging_config import setup_logging

logger = setup_logging(name="publisher")


async def publish_event(event: OutboxEventDTO, publisher: IMessagePublisher):
    try:
        logger.info(f"Enviando evento {event.event_type} : {event.payload}")
        await publisher.publish({
            "order_id": str(event.order_id),
            "event_type": event.event_type,
            "payload": event.payload
        })
        logger.info(f"Evento {event.event_type} enviado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao enviar evento: {e}")
        raise

async def process_outbox(outbox_repo : IOutboxEventRepository, publisher: IMessagePublisher):
    while True:
        events = await outbox_repo.get_pending_events()
        for event in events:
            logger.info(f"Processando evento: id={event.id} type={event.event_type}")
            await publish_event(event, publisher)
            await outbox_repo.mark_event_sent(event.id)
        await asyncio.sleep(2)  # intervalo entre batches

async def main():
    publisher = get_event_publisher()
    outbox_repo = get_outbox_event_repository()
    await process_outbox(outbox_repo, publisher)

if __name__ == "__main__":
    asyncio.run(main())