import instructor

from yalc.clients.client import Client
from yalc.clients.provider_clients.anthropic import AnthropicClient
from yalc.clients.provider_clients.openai import OpenAIClient
from yalc.clients.strategy import ClientMetadataStrategy
from yalc.common.schemas import LLMModel, LLMProvider

provider_to_client_map: dict[LLMProvider, type[Client]] = {
    LLMProvider.OPENAI: OpenAIClient,
    LLMProvider.ANTHROPIC: AnthropicClient,
}


def create_client(
    model: LLMModel,
    metadata_strategies: list[ClientMetadataStrategy] = [],
) -> Client:
    client_class = provider_to_client_map.get(model.provider)
    if client_class is None:
        raise ValueError(f"Unsupported provider: {model.provider}")

    instructor_client = instructor.from_provider(
        model.provider_string,
        async_client=True,
        mode=model.mode,
    )
    return client_class(model, instructor_client, metadata_strategies)
