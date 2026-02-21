from unittest.mock import AsyncMock

import pytest
from anthropic.types import Message, Usage
from pydantic import BaseModel

from yalc.clients.provider_clients.anthropic import AnthropicClient
from yalc.clients.schemas import ClientCall
from yalc.common.schemas import LLMModel, LLMRole


class SimpleResponse(BaseModel):
    text: str


def fake_anthropic_response(
    input_tokens: int, output_tokens: int
) -> Message:
    return Message(
        id="msg_1",
        content=[],
        model="claude-sonnet-4-5",
        role="assistant",
        stop_reason="end_turn",
        type="message",
        usage=Usage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        ),
    )


@pytest.mark.anyio
async def test_anthropic_client_structured_response(
    anthropic_client: AnthropicClient,
    mock_pricing,
):
    # Arrange
    parsed = SimpleResponse(text="hello")
    raw_response = fake_anthropic_response(
        input_tokens=10, output_tokens=5
    )
    # Mock instructor
    anthropic_client.instructor_client.messages.create_with_completion = AsyncMock(
        return_value=(parsed, raw_response)
    )
    messages = [{"role": "user", "content": "Say hello"}]

    # Act
    result, call = await anthropic_client.structured_response(
        SimpleResponse, messages
    )

    # Assert
    assert result.text == "hello"
    assert isinstance(call, ClientCall)
    assert call.model_name == LLMModel.claude_sonnet_4_5
    assert call.input_tokens == 10
    assert call.output_tokens == 5
    assert call.input_tokens_cost == 10 * 0.0003
    assert call.output_tokens_cost == 5 * 0.0006
    assert len(call.context_messages) == 1
    assert call.context_messages[0].message == "Say hello"
    assert call.context_messages[0].role == LLMRole.USER
    assert call.client_message.role == LLMRole.ASSISTANT
    assert call.client_message.response == result
