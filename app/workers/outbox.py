import asyncio
import json
from aio_pika import connect_robust, ExchangeType, Message
from app.db.database import AsyncSessionLocal
from app.models.outbox_event import OutboxEvent
from app.core.config import settings
from sqlalchemy import select, update
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

async def publish_event(event: OutboxEvent):
    try:
        logging.info(f"Enviando evento {event.event_type} para RabbitMQ: {event.payload}")
        connection = await connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()

        exchange = await channel.declare_exchange("delivery_events", ExchangeType.FANOUT)
        message_body = json.dumps(event.payload).encode()
        message = Message(message_body, type=event.event_type)
        await exchange.publish(message, routing_key="")
        await connection.close()
        logging.info(f"Evento {event.event_type} enviado com sucesso")
    except Exception as e:
        logging.error(f"Erro ao enviar evento: {e}")
        raise

async def process_outbox():
    while True:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(OutboxEvent).where(OutboxEvent.sent == False).order_by(OutboxEvent.created_at)
            )
            events = result.scalars().all()

            #if not events:
                #logging.info("Nenhum evento pendente encontrado.")
            for event in events:
                logging.info(f"Processando evento: id={event.id} type={event.event_type}")
                await publish_event(event)
                # Marca como enviado na tabela outbox_events
                await session.execute(
                    update(OutboxEvent).where(OutboxEvent.id == event.id).values(sent=True)
                )
            await session.commit()
        await asyncio.sleep(2)  # intervalo entre batches

if __name__ == "__main__":
    asyncio.run(process_outbox())