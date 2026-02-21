from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from yalc.clients.schemas import ClientCall

T = TypeVar("T", bound=BaseModel)


class ClientMetadataStrategy(ABC, Generic[T]):
    @abstractmethod
    def handle(self, call: ClientCall, context: T | None):
        pass
