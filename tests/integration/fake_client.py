from pydantic import BaseModel

from yalc.clients.client import Client
from yalc.common.pricing import PricingService
from yalc.common.schemas import LLMModel, ResponseStats


class FakeRawResponse(BaseModel):
    input_tokens: int
    output_tokens: int


class FakeClient(Client):
    def __init__(self):
        self.metadata_strategies = []
        self.pricing_service = PricingService()
        self.model = LLMModel.gpt_4o_mini

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
