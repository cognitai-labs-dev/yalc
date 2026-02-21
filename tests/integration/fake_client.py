from dataclasses import dataclass
from unittest.mock import MagicMock

from pydantic import BaseModel

from yalc.clients.client import Client
from yalc.common.schemas import LLMModel, ResponseStats


@dataclass
class FakeRawResponse:
    input_tokens: int
    output_tokens: int


class FakeClient(Client):
    def __init__(self):
        super().__init__(LLMModel.gpt_4o_mini, MagicMock())

    async def _response[T: BaseModel](
        self,
        response_type: type[T],
        messages: list[dict[str, str]],
    ) -> tuple[T, FakeRawResponse]:
        parsed = response_type(text="hello")  # type: ignore[call-arg]
        return parsed, FakeRawResponse(
            input_tokens=10, output_tokens=5
        )

    def _get_response_stats(
        self, response: FakeRawResponse
    ) -> ResponseStats:
        return self.pricing_service.build_response_stats(
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            model=self.model,
        )
