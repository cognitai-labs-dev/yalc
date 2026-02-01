from cachetools import TTLCache, cached
from litellm import model_cost_map_url
from litellm.litellm_core_utils.get_model_cost_map import (
    get_model_cost_map,
)

from src.common.schemas import LLMModel, ResponseStats, TokensPricing


class PricingService:
    def build_response_stats(
        self,
        input_tokens: int,
        output_tokens: int,
        model: LLMModel,
    ) -> ResponseStats:
        return ResponseStats(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_tokens_cost=self._get_input_token_cost(
                model.value, input_tokens
            ),
            output_tokens_cost=self.get_output_token_cost(
                model.value, output_tokens
            ),
        )

    def _get_input_token_cost(
        self, model: str, input_tokens: int
    ) -> float:
        model_pricing = self._get_model_pricing(model)
        return input_tokens * model_pricing.input_cost_per_token

    def get_output_token_cost(
        self, model: str, output_tokens: int
    ) -> float:
        model_pricing = self._get_model_pricing(model)
        return output_tokens * model_pricing.output_cost_per_token

    @staticmethod
    @cached(cache=TTLCache(maxsize=100, ttl=60 * 5))  # 5 minute TTL
    def _get_model_pricing(model: str) -> TokensPricing:
        """
        Cache the result for 5 minutes since every function call makes
        a http request
        """
        model_cost = get_model_cost_map(model_cost_map_url)
        if model not in model_cost:
            raise ValueError(
                f"Model {model} not found in litellm pricing data"
            )

        pricing = model_cost[model]
        return TokensPricing(
            input_cost_per_token=pricing.get(
                "input_cost_per_token", 0
            ),
            output_cost_per_token=pricing.get(
                "output_cost_per_token", 0
            ),
        )
