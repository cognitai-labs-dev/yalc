from unittest.mock import AsyncMock

import pytest
from openai.types.responses import Response
from openai.types.responses.response_usage import (
    InputTokensDetails,
    OutputTokensDetails,
    ResponseUsage,
)
from pydantic import BaseModel

from yalc.clients.provider_clients.openai import OpenAIClient
from yalc.clients.schemas import ClientCall
from yalc.common.schemas import LLMModel, LLMRole


class SimpleResponse(BaseModel):
    text: str


def fake_openai_response(
    input_tokens: int, output_tokens: int
) -> Response:
    return Response(
        id="resp_1",
        created_at=0,
        model="gpt-4o-mini",
        object="response",
        output=[],
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
        usage=ResponseUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            input_tokens_details=InputTokensDetails(cached_tokens=0),
            output_tokens_details=OutputTokensDetails(
                reasoning_tokens=0
            ),
        ),
    )


@pytest.mark.anyio
async def test_openai_client_structured_response(
    openai_client: OpenAIClient,
    mock_pricing,
):
    # Arrange
    parsed = SimpleResponse(text="hello")
    raw_response = fake_openai_response(
        input_tokens=10, output_tokens=5
    )
    openai_client.instructor_client.responses.create_with_completion = AsyncMock(
        return_value=(parsed, raw_response)
    )
    messages = [{"role": "user", "content": "Say hello"}]

    # Act
    result, call = await openai_client.structured_response(
        SimpleResponse, messages
    )

    # Assert
    assert result.text == "hello"
    assert isinstance(call, ClientCall)
    assert call.model_name == LLMModel.gpt_4o_mini
    assert call.input_tokens == 10
    assert call.output_tokens == 5
    assert call.input_tokens_cost == 10 * 0.0001
    assert call.output_tokens_cost == 5 * 0.0002
    assert len(call.context_messages) == 1
    assert call.context_messages[0].message == "Say hello"
    assert call.context_messages[0].role == LLMRole.USER
    assert call.client_message.role == LLMRole.ASSISTANT
    assert call.client_message.response == result
