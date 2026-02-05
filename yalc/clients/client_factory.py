from yalc.clients.client import Client
from yalc.clients.provider_clients.anthropic import AnthropicClient
from yalc.clients.provider_clients.openai import OpenAIClient
from yalc.clients.strategy import ClientLogStrategy
from yalc.common.schemas import LLMModel, LLMProvider

provider_to_client_map: dict[LLMProvider, type[Client]] = {
    LLMProvider.OPENAI: OpenAIClient,
    LLMProvider.ANTHROPIC: AnthropicClient,
}


def create_client(
    model: LLMModel,
    log_strategies: list[ClientLogStrategy] = [],
) -> Client:
    client_class = provider_to_client_map.get(model.provider)
    if client_class is None:
        raise ValueError(f"Unsupported provider: {model.provider}")
    return client_class(model, log_strategies)
