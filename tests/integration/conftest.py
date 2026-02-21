import pytest
from pytest_mock import MockerFixture

from yalc.common.pricing import PricingService


@pytest.fixture
def mock_pricing(mocker: MockerFixture) -> None:
    """Patches the HTTP call that fetches LLM pricing data."""
    mocker.patch(
        "yalc.common.pricing.get_model_cost_map",
        return_value={
            "gpt-4o-mini": {
                "input_cost_per_token": 0.0001,
                "output_cost_per_token": 0.0002,
            }
        },
    )
