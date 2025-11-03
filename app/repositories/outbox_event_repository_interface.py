from abc import ABC, abstractmethod
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

class IOutboxEventRepository(ABC):
    @abstractmethod
    async def create(self, session: AsyncSession, order_id: Any, event_type: str, payload: dict):
        """Cria um novo registro OutboxEvent usando a sessão fornecida."""
        pass

    @abstractmethod
    async def get_pending_events(self) -> list:
        """Retorna uma lista de eventos OutboxEvent pendentes."""
        pass

    @abstractmethod
    async def mark_event_sent(self, event_id: Any) -> None:
        """Marca um evento OutboxEvent como enviado."""
        pass
        """Cria um novo registro OutboxEvent usando a sessão fornecida."""
        pass