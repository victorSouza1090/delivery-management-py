from abc import ABC, abstractmethod
from typing import Callable, Awaitable, Any

class IMessageWorker(ABC):
    @abstractmethod
    async def start(self, handler: Callable[[dict], Awaitable[None]]):
        """
        Inicia o worker e chama handler para cada mensagem recebida.
        """
        raise NotImplementedError
    

class IMessagePublisher(ABC):
    @abstractmethod
    async def publish(self, event: dict[str, Any]):
        """
        Publica um evento na mensageria.
        O evento deve ser um dict serializável em JSON.
        """
        raise NotImplementedError
