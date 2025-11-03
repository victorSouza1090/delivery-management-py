import asyncio
import logging
from app.models.outbox_event import OutboxEvent
from app.dependencies import get_event_publisher, get_outbox_event_repository
from app.repositories.outbox_event_repository_interface import IOutboxEventRepository
from app.workers.interfaces import IMessagePublisher

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")


async def publish_event(event: OutboxEvent, publisher: IMessagePublisher):
    try:
        logging.info(f"Enviando evento {event.event_type} : {event.payload}")
        await publisher.publish({
            "order_id": str(event.order_id),
            "event_type": event.event_type,
            "payload": event.payload
        })
        logging.info(f"Evento {event.event_type} enviado com sucesso")
    except Exception as e:
        logging.error(f"Erro ao enviar evento: {e}")
        raise

async def process_outbox(outbox_repo : IOutboxEventRepository, publisher: IMessagePublisher):
    while True:
        events = await outbox_repo.get_pending_events()
        for event in events:
            logging.info(f"Processando evento: id={event.id} type={event.event_type}")
            await publish_event(event, publisher)
            await outbox_repo.mark_event_sent(event.id)
        await asyncio.sleep(2)  # intervalo entre batches

async def main():
    publisher = get_event_publisher()
    outbox_repo = get_outbox_event_repository()
    await process_outbox(outbox_repo, publisher)

if __name__ == "__main__":
    asyncio.run(main())