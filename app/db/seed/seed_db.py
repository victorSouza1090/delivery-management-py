import asyncio
import uuid
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.order import Order, OrderStatus
from app.models.order_event import OrderEvent

# Dados de teste
ORDERS_TO_INSERT = [
    {"customer_name": "João Silva", "address": "Rua A, 123"},
    {"customer_name": "Maria Souza", "address": "Av. B, 456"},
    {"customer_name": "Carlos Lima", "address": "Travessa C, 789"},
]

async def seed_orders():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for order_data in ORDERS_TO_INSERT:
                result = await session.execute(
                    select(Order).where(
                        (Order.customer_name == order_data["customer_name"]) &
                        (Order.address == order_data["address"])
                    )
                )
                existing_order = result.scalar_one_or_none()

                if existing_order:
                    print(f"Pedido já existe: {existing_order.customer_name}")
                    continue

                new_order = Order(
                    id=str(uuid.uuid4()),
                    customer_name=order_data["customer_name"],
                    address=order_data["address"],
                    status=OrderStatus.RECEIVED
                )
                session.add(new_order)
                await session.flush()  # Gera o ID do pedido

                new_event = OrderEvent(
                    id=str(uuid.uuid4()),
                    order_id=new_order.id,
                    status=OrderStatus.RECEIVED
                )
                session.add(new_event)
        await session.commit()
        print("Seed de pedidos concluído!")

if __name__ == "__main__":
    asyncio.run(seed_orders())
