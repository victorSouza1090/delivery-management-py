from abc import ABC, abstractmethod
from uuid import UUID
from app.models.order import Order
from app.models.order_event import OrderEvent

class IOrderRepository(ABC):
    """Interface para o repositório de pedidos.

    Define os métodos que qualquer implementação concreta deve fornecer
    para criar, consultar pedidos e acessar seus eventos.
    """

    @abstractmethod
    async def create_order(self, customer_name: str, address: str) -> Order:
        """
        Cria uma nova ordem de entrega e persiste no banco,
        incluindo o evento inicial de status 'RECEIVED'.

        Args:
            customer_name (str): Nome do cliente.
            address (str): Endereço de entrega.

        Returns:
            Order: Objeto Order criado com ID e status inicial.
        """
        pass

    @abstractmethod
    async def get_order_by_id(self, order_id: UUID) -> Order | None:
        """
        Busca uma ordem pelo seu ID.

        Args:
            order_id (UUID): ID do pedido a ser consultado.

        Returns:
            Order | None: Objeto Order se encontrado, ou None se não existir.
        """
        pass

    @abstractmethod
    async def get_order_events(self, order_id: UUID) -> list[OrderEvent]:
        """
        Retorna todos os eventos associados a um pedido específico,
        ordenados pela data/hora do evento.

        Args:
            order_id (UUID): ID do pedido.

        Returns:
            list[OrderEvent]: Lista de eventos do pedido.
        """
        pass
    
    @abstractmethod
    async def update_order_status(self, order_id: UUID, new_status: 'OrderStatus') -> None:
        """
        Atualiza o status de um pedido e registra o evento correspondente.

        Args:
            order_id (UUID): ID do pedido a ser atualizado.
            new_status (OrderStatus): Novo status a ser definido.

        Returns:
            None
        """
        pass