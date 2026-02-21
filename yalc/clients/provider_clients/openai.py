from openai.types.responses import Response
from pydantic import BaseModel

from yalc.clients.client import Client
from yalc.common.schemas import LLMProvider, ResponseStats


@Client.provider(LLMProvider.OPENAI)
class OpenAIClient(Client):
    async def _response[T: BaseModel](
        self,
        response_type: type[T],
        messages: list[dict[str, str]],
    ) -> tuple[T, Response]:
        return await self.instructor_client.responses.create_with_completion(  # type: ignore
            model=self.model.value,
            response_model=response_type,
            max_retries=3,
            input=messages,  # type: ignore
        )

    def _get_response_stats(
        self, response: Response
    ) -> ResponseStats:
        if response.usage is None:
            raise RuntimeError("no usage for llm call")

        return self.pricing_service.build_response_stats(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model=self.model,
        )
