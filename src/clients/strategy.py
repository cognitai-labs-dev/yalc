from abc import ABC, abstractmethod

from pydantic import BaseModel

from src.clients.schemas import ClientCall


class ClientLogStrategy[T: BaseModel](ABC):
    @abstractmethod
    def handle(self, call: ClientCall, context: T | None):
        pass
