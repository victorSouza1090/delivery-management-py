import uuid
from uuid import UUID
from sqlalchemy import select
from app.repositories.order_repository_interface import IOrderRepository
from app.repositories.outbox_event_repository_interface import IOutboxEventRepository
from app.db.database import AsyncSessionLocal
from app.models.order import Order, OrderStatus
from app.models.order_event import OrderEvent

class OrderRepository(IOrderRepository):
    """Implementação concreta do repositório de pedidos"""
    def __init__(self, outbox_repo, session_factory=AsyncSessionLocal):
        self.outbox_repo = outbox_repo
        self.session_factory = session_factory

    async def create_order(self, customer_name: str, address: str) -> Order:
        async with self.session_factory() as session:
            async with session.begin():
                order_id = uuid.uuid4()
                order = Order(
                    id=str(order_id),
                    customer_name=customer_name,
                    address=address,
                    status=OrderStatus.RECEIVED
                )
                session.add(order)
                await session.flush() 

                await self._add_order_event(session, order_id, OrderStatus.RECEIVED)
                
                # Inserir no outbox
                await self.outbox_repo.create(session, str(order_id), "OrderCreated", {
                    "order_id": str(order_id),
                    "status": order.status.value
                })

            await session.commit()
            return order

    async def update_order_status(self, order_id: UUID, new_status: OrderStatus) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                order = await self._get_order(session, order_id)
                if not await self._should_update_status(order, new_status, session):
                    return
                order.status = new_status
                await self._add_order_event(session, uuid.UUID(order.id), new_status)
                
                # Inserir no outbox
                await self.outbox_repo.create(session, order.id, "OrderStatusUpdated", {
                    "order_id": order.id,
                    "status": new_status.value
                })
            await session.commit()

    async def _get_order(self, session, order_id: UUID) -> Order | None:
        result = await session.execute(select(Order).where(Order.id == str(order_id)))
        return result.scalar_one_or_none()

    async def _should_update_status(self, order: Order | None, new_status: OrderStatus, session) -> bool:
        if not order:
            return False
        if order.status == new_status:
            return False
        event_exists = await session.execute(
            select(OrderEvent).where(
                OrderEvent.order_id == order.id,
                OrderEvent.status == new_status
            )
        )
        if event_exists.scalar_one_or_none():
            return False
        return True

    async def _add_order_event(self, session, order_id: UUID, status: OrderStatus) -> None:
        event = OrderEvent(
            id=str(uuid.uuid4()),
            order_id=str(order_id),
            status=status
        )
        session.add(event)
            
    async def get_order_by_id(self, order_id: UUID) -> Order | None:
        async with self.session_factory() as session:
            result = await session.execute(select(Order).where(Order.id == str(order_id)))
            return result.scalar_one_or_none()

    async def get_order_events(self, order_id: UUID) -> list[OrderEvent]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(OrderEvent)
                .where(OrderEvent.order_id == str(order_id))
                .order_by(OrderEvent.timestamp)
            )
            return result.scalars().all()