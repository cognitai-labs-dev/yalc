from abc import ABC, abstractmethod
from typing import Any, overload

import instructor
from pydantic import BaseModel

from src.clients.schemas import ClientCall, ClientMessage
from src.clients.strategy import ClientLogStrategy
from src.common.pricing import PricingService
from src.common.schemas import LLMModel, LLMRole, ResponseStats
from src.common.utils import to_context_messages


class Client(ABC):
    def __init__(
        self,
        model: LLMModel,
        log_strategies: list[ClientLogStrategy] = [],
    ):
        self.log_strategies = log_strategies
        self.pricing_service = PricingService()

        self.instructor_client = instructor.from_provider(
            model.provider_string,
            async_client=True,
            mode=model.mode,
        )
        self.model = model

    @overload
    async def structured_response[T: BaseModel](
        self,
        response_type: type[T],
        messages: list[dict[str, str]],
        context: BaseModel,
    ) -> T: ...

    @overload
    async def structured_response[T: BaseModel](
        self,
        response_type: type[T],
        messages: list[dict[str, str]],
    ) -> tuple[T, BaseModel]: ...

    async def structured_response[T: BaseModel](
        self,
        response_type: type[T],
        messages: list[dict[str, str]],
        context: BaseModel | None = None,
    ) -> T | tuple[T, BaseModel]:
        """
        Provides a structured response via an LLM call

        Uses provided log strategies to log all the LLM messages
        """
        response, llm_call = await self._structured_response(
            response_type, messages
        )

        if context is not None:
            for strategy in self.log_strategies:
                strategy.handle(llm_call, context)
            return response

        return response, llm_call

    async def _structured_response[T: BaseModel](
        self,
        response_type: type[T],
        messages: list[dict[str, str]],
    ) -> tuple[T, ClientCall]:
        parsed, response = await self._response(
            response_type, messages
        )

        llm_call = self._create_llm_call(messages, parsed, response)
        return parsed, llm_call

    def _create_llm_call(
        self,
        messages: list[dict[str, str]],
        parsed: BaseModel,
        response: Any,
    ) -> ClientCall:
        context_messages = to_context_messages(messages)
        client_message = self._parse_client_message(parsed)

        return ClientCall(
            context_messages=context_messages,
            client_message=client_message,
            model_name=self.model,
            **self._get_response_stats(response).model_dump(),
        )

    @staticmethod
    def _parse_client_message(parsed: BaseModel) -> ClientMessage:
        return ClientMessage(response=parsed, role=LLMRole.ASSISTANT)

    @abstractmethod
    async def _response[T: BaseModel](
        self,
        response_type: type[T],
        messages: list[dict[str, str]],
    ) -> tuple[T, Any]:
        pass

    @abstractmethod
    def _get_response_stats(self, response: Any) -> ResponseStats:
        pass
