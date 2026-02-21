from abc import ABC, abstractmethod

from pydantic import BaseModel

from yalc.clients.schemas import ClientCall


class ClientMetadataStrategy[T: BaseModel](ABC):
    """Abstract strategy for handling LLM call metadata (e.g. logging, persistence).

    Subclass this and implement :meth:`handle` to define custom behaviour that runs
    after each LLM call when a ``context`` object is passed to
    :meth:`~yalc.clients.client.Client.structured_response`.
    """

    @abstractmethod
    def handle(self, call: ClientCall, context: T | None):
        pass
