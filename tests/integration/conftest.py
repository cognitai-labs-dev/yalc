from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from yalc.clients.provider_clients.anthropic import AnthropicClient
from yalc.clients.provider_clients.openai import OpenAIClient
from yalc.common.schemas import LLMModel


@pytest.fixture
def mock_pricing(mocker: MockerFixture) -> None:
    """Patches the HTTP call that fetches LLM pricing data."""
    mocker.patch(
        "yalc.common.pricing.get_model_cost_map",
        return_value={
            "gpt-4o-mini": {
                "input_cost_per_token": 0.0001,
                "output_cost_per_token": 0.0002,
            },
            "claude-sonnet-4-5": {
                "input_cost_per_token": 0.0003,
                "output_cost_per_token": 0.0006,
            },
        },
    )


@pytest.fixture
def openai_client() -> OpenAIClient:
    """OpenAIClient with a fake instructor client injected."""
    return OpenAIClient(LLMModel.gpt_4o_mini, MagicMock())


@pytest.fixture
def anthropic_client() -> AnthropicClient:
    """AnthropicClient with a fake instructor client injected."""
    return AnthropicClient(LLMModel.claude_sonnet_4_5, MagicMock())


@pytest.fixture
def mock_instructor(mocker: MockerFixture) -> None:
    """Patches the instructor client so no API keys are needed."""
    mocker.patch(
        "yalc.clients.client_factory.instructor.from_provider"
    )
