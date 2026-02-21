import pytest
from pydantic import BaseModel

from tests.integration.fake_client import FakeClient
from yalc.clients.schemas import ClientCall
from yalc.clients.strategy import ClientMetadataStrategy
from yalc.common.schemas import LLMModel, LLMRole


class SimpleResponse(BaseModel):
    text: str


class SimpleContext(BaseModel):
    user_id: int


@pytest.mark.anyio
async def test_client_with_returned_client_call(mock_pricing):
    # Arrange
    client = FakeClient()
    messages = [{"role": "user", "content": "Say hello"}]

    # Act
    result, call = await client.structured_response(
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


@pytest.mark.anyio
async def test_client_calls_strategy_and_returns_parsed_response(
    mock_pricing,
):
    # Arrange
    recorded: list[tuple[ClientCall, SimpleContext]] = []

    class RecordingStrategy(ClientMetadataStrategy):
        def handle(self, call: ClientCall, context: SimpleContext):
            recorded.append((call, context))

    client = FakeClient()
    client.metadata_strategies = [RecordingStrategy()]
    context = SimpleContext(user_id=42)
    messages = [{"role": "user", "content": "Say hello"}]

    # Act
    result = await client.structured_response(
        SimpleResponse, messages, context
    )

    # Assert — only parsed response is returned, not a tuple
    assert isinstance(result, SimpleResponse)
    assert result.text == "hello"

    # Assert — strategy was called with the ClientCall and context
    assert len(recorded) == 1
    call, received_context = recorded[0]
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
    assert received_context == context
