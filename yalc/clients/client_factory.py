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
    """Create and return a provider-specific :class:`~yalc.clients.client.Client` for the given model.

    Args:
        model: The LLM model to use. Determines which provider client is instantiated.
        metadata_strategies: Optional list of strategies invoked after each call when a
            context object is supplied to ``structured_response``.

    Returns:
        A ready-to-use async ``Client`` instance configured for the specified model.

    Raises:
        ValueError: If the model's provider is not supported.
    """
    client_class = provider_to_client_map.get(model.provider)
    if client_class is None:
        raise ValueError(f"Unsupported provider: {model.provider}")

    instructor_client = instructor.from_provider(
        model.provider_string,
        async_client=True,
        mode=model.mode,
    )
    return client_class(model, instructor_client, metadata_strategies)
