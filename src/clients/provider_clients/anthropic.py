from anthropic.types import Message
from pydantic import BaseModel

from src.clients.client import Client
from src.common.schemas import ResponseStats


class AnthropicClient(Client):
    async def _response[T: BaseModel](
        self,
        response_type: type[T],
        messages: list[dict[str, str]],
    ) -> tuple[T, Message]:
        return await self.instructor_client.messages.create_with_completion(  # type: ignore
            model=self.model.value,
            response_model=response_type,
            max_retries=3,
            messages=messages,  # type: ignore
        )

    def _get_response_stats(self, response: Message) -> ResponseStats:
        return self.pricing_service.build_response_stats(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model=self.model,
        )
