from yalc.clients.client_factory import create_client
from yalc.clients.provider_clients.anthropic import AnthropicClient
from yalc.clients.provider_clients.openai import OpenAIClient
from yalc.common.schemas import LLMModel


def test_create_client_returns_openai_client_for_openai_model(
    mock_instructor,
):
    client = create_client(LLMModel.gpt_4o_mini)
    assert isinstance(client, OpenAIClient)


def test_create_client_returns_anthropic_client_for_anthropic_model(
    mock_instructor,
):
    client = create_client(LLMModel.claude_sonnet_4_5)
    assert isinstance(client, AnthropicClient)
