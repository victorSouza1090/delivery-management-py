from app.schemas.order_schema import OrderCreate, OrderResponse, OrderEventResponse
from app.repositories.order_repository_interface import IOrderRepository
from uuid import UUID

class OrderService:
    """Serviço responsável pela lógica de negócios de pedidos."""

    def __init__(self, order_repo: IOrderRepository):
        self.order_repo = order_repo

    async def create_order(self, order: OrderCreate) -> OrderResponse:
        """
        Cria um novo pedido e retorna os dados no schema OrderResponse.

        Args:
            order (OrderCreate): Dados do pedido a ser criado.

        Returns:
            OrderResponse: Pedido criado.
        """
        new_order = await self.order_repo.create_order(
            customer_name=order.customer_name,
            address=order.address
        )
        return OrderResponse(
            id=str(new_order.id),
            customer_name=new_order.customer_name,
            address=new_order.address,
            status=new_order.status.value,  # caso OrderStatus seja Enum
            created_at=new_order.created_at
        )

    async def get_order(self, order_id: UUID) -> OrderResponse:
        """
        Busca um pedido pelo ID e retorna os dados no schema OrderResponse.

        Args:
            order_id (str): ID do pedido a ser buscado.

        Returns:
            OrderResponse: Pedido encontrado.

        Raises:
            ValueError: Se o pedido não existir.
        """
        order = await self.order_repo.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        return OrderResponse(
            id=str(order.id),
            customer_name=order.customer_name,
            address=order.address,
            status=order.status.value,  # caso OrderStatus seja Enum
            created_at=order.created_at
        )

    async def get_order_events(self, order_id: UUID) -> list[OrderEventResponse]:
        """
        Retorna todos os eventos de um pedido específico.

        Args:
            order_id (str): ID do pedido.

        Returns:
            List[OrderEventResponse]: Lista de eventos do pedido.
        """
        events = await self.order_repo.get_order_events(order_id)
        return [
            OrderEventResponse(
                id=str(event.id),
                order_id=str(event.order_id),
                status=event.status.value,
                timestamp=event.timestamp
            )
            for event in events
        ]