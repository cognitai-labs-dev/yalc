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
async def test_client_calls_all_strategies_and_returns_parsed_response(
    mock_pricing,
):
    # Arrange
    recorded: list[tuple[str, ClientCall, SimpleContext]] = []

    class StrategyA(ClientMetadataStrategy[SimpleContext]):
        def handle(
            self, call: ClientCall, context: SimpleContext | None
        ):
            if context is None:
                return
            recorded.append(("a", call, context))

    class StrategyB(ClientMetadataStrategy[SimpleContext]):
        def handle(
            self, call: ClientCall, context: SimpleContext | None
        ):
            if context is None:
                return
            recorded.append(("b", call, context))

    client = FakeClient()
    client.metadata_strategies = [StrategyA(), StrategyB()]
    context = SimpleContext(user_id=42)
    messages = [{"role": "user", "content": "Say hello"}]

    # Act
    result = await client.structured_response(
        SimpleResponse, messages, context
    )

    # Assert — only parsed response is returned, not a tuple
    assert isinstance(result, SimpleResponse)
    assert result.text == "hello"

    # Assert — both strategies were called in order with the ClientCall and context
    assert len(recorded) == 2

    strategy_a, call_a, context_a = recorded[0]
    strategy_b, call_b, context_b = recorded[1]

    assert strategy_a == "a"
    assert strategy_b == "b"

    assert isinstance(call_a, ClientCall)
    assert call_a.model_name == LLMModel.gpt_4o_mini
    assert call_a.input_tokens == 10
    assert call_a.output_tokens == 5
    assert call_a.input_tokens_cost == 10 * 0.0001
    assert call_a.output_tokens_cost == 5 * 0.0002
    assert len(call_a.context_messages) == 1
    assert call_a.context_messages[0].message == "Say hello"
    assert call_a.context_messages[0].role == LLMRole.USER
    assert call_a.client_message.role == LLMRole.ASSISTANT
    assert call_a.client_message.response == result
    assert context_a == context

    assert call_b == call_a
    assert context_b == context
