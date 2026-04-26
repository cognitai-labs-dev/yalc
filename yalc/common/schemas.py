from enum import StrEnum
from typing import NamedTuple

import instructor
from pydantic import BaseModel


class LLMRole(StrEnum):
    """Role of a participant in an LLM conversation."""

    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"
    TOOL = "tool"


class ResponseStats(BaseModel):
    """Token usage and cost statistics for a single LLM call."""

    input_tokens: int
    output_tokens: int
    input_tokens_cost: float
    output_tokens_cost: float


class ContextMessage(BaseModel):
    """A single message in a conversation, with its role and text content."""

    message: str
    role: LLMRole


class TokensPricing(NamedTuple):
    input_cost_per_token: float
    output_cost_per_token: float


class LLMProvider(StrEnum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"


provider_to_mode_map = {
    LLMProvider.OPENAI: instructor.Mode.RESPONSES_TOOLS,
    LLMProvider.ANTHROPIC: instructor.Mode.ANTHROPIC_TOOLS,
}


class LLMModel(StrEnum):
    """Supported LLM models.

    Each value is the canonical model ID string used when calling the provider API.
    """

    gpt_4o_mini = "gpt-4o-mini"
    gpt_5_mini = "gpt-5-mini"
    gpt_5_nano = "gpt-5-nano"
    gpt_5_2 = "gpt-5.2"
    gpt_5_2_codex = "gpt-5.2-codex"
    gpt_5_4 = "gpt-5.4"
    gpt_5_4_mini = "gpt-5.4-mini"
    gpt_5_4_nano = "gpt-5.4-nano"

    claude_haiku_4_5 = "claude-haiku-4-5"
    claude_sonnet_4_5 = "claude-sonnet-4-5"
    claude_sonnet_4_6 = "claude-sonnet-4-6"
    claude_opus_4_6 = "claude-opus-4-6"
    claude_opus_4_7 = "claude-opus-4-7"

    @property
    def provider(self) -> LLMProvider:
        return model_to_provider_map[self]

    @property
    def provider_string(self) -> str:
        return f"{self.provider.value}/{self.value}"

    @property
    def mode(self) -> instructor.Mode:
        return provider_to_mode_map[self.provider]


model_to_provider_map: dict[LLMModel, LLMProvider] = {
    LLMModel.gpt_4o_mini: LLMProvider.OPENAI,
    LLMModel.gpt_5_mini: LLMProvider.OPENAI,
    LLMModel.gpt_5_nano: LLMProvider.OPENAI,
    LLMModel.gpt_5_2: LLMProvider.OPENAI,
    LLMModel.gpt_5_2_codex: LLMProvider.OPENAI,
    LLMModel.gpt_5_4_mini: LLMProvider.OPENAI,
    LLMModel.gpt_5_4: LLMProvider.OPENAI,
    LLMModel.gpt_5_4_nano: LLMProvider.OPENAI,
    LLMModel.claude_haiku_4_5: LLMProvider.ANTHROPIC,
    LLMModel.claude_sonnet_4_5: LLMProvider.ANTHROPIC,
    LLMModel.claude_sonnet_4_6: LLMProvider.ANTHROPIC,
    LLMModel.claude_opus_4_6: LLMProvider.ANTHROPIC,
    LLMModel.claude_opus_4_7: LLMProvider.ANTHROPIC,
}
