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
    The provider is declared inline as a second argument.
    """

    gpt_4o_mini = "gpt-4o-mini", LLMProvider.OPENAI
    gpt_5_mini = "gpt-5-mini", LLMProvider.OPENAI
    gpt_5_nano = "gpt-5-nano", LLMProvider.OPENAI
    gpt_5_2 = "gpt-5.2", LLMProvider.OPENAI
    gpt_5_3_codex = "gpt-5.2-codex", LLMProvider.OPENAI

    claude_haiku_4_5 = "claude-haiku-4-5", LLMProvider.ANTHROPIC
    claude_sonnet_4_5 = "claude-sonnet-4-5", LLMProvider.ANTHROPIC
    claude_sonnet_4_6 = "claude-sonnet-4-6", LLMProvider.ANTHROPIC
    claude_opus_4_6 = "claude-opus-4-6", LLMProvider.ANTHROPIC

    def __new__(cls, value: str, provider: LLMProvider) -> "LLMModel":
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj._provider = provider  # type: ignore[attr-defined]
        return obj

    @property
    def provider(self) -> LLMProvider:
        return self._provider  # type: ignore[attr-defined]

    @property
    def provider_string(self) -> str:
        return f"{self.provider.value}/{self.value}"

    @property
    def mode(self) -> instructor.Mode:
        return provider_to_mode_map[self.provider]
