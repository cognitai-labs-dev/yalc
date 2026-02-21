# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run tests
make test

# Run a specific test file or directory
uv run pytest tests/path/to/test.py -v

# Lint (ruff check + format + mypy via pre-commit)
make lint

# Individual lint steps
make ruff-lint    # ruff check --fix
make ruff-format  # ruff format
make mypy         # mypy type checking
```

The project uses `uv` for dependency management. Run commands with `uv run <cmd>`.

## Architecture

YALC is a thin async Python wrapper over the [instructor](https://python.useinstructor.com/) library, enforcing pydantic-serialized responses from LLM calls across multiple providers.

**Core flow:**

1. `create_client(model, metadata_strategies)` — factory that maps `LLMModel` → provider-specific `Client` subclass
2. `Client.structured_response(response_type, messages, context?)` — public API; calls the provider, builds a `ClientCall`, then either:
   - Returns `(parsed, ClientCall)` tuple if no `context` is given
   - Invokes all `ClientMetadataStrategy.handle(call, context)` instances and returns just the parsed response
3. Provider clients (`AnthropicClient`, `OpenAIClient`) implement `_response()` and `_get_response_stats()` using the instructor async client
4. `PricingService` fetches per-token pricing from litellm's cost map (TTL-cached 5 min) and computes costs in `ResponseStats`

**Key types (all exported from `yalc/__init__.py`):**

- `LLMModel` (StrEnum) — model IDs; has `.provider`, `.provider_string`, `.mode` properties
- `ClientCall` — full record of an LLM call: token counts, costs, model name, input messages, parsed response
- `ClientMetadataStrategy[T]` — abstract base; implement `handle(call: ClientCall, context: T)` to define custom logging/persistence
- `ContextMessage` / `ClientMessage` — message wrappers for conversation history and LLM replies

**Adding a new provider:** add an entry to `model_to_provider_map` and `provider_to_mode_map` in `yalc/common/schemas.py`, create a subclass of `Client` in `yalc/clients/provider_clients/`, and register it in `provider_to_client_map` in `yalc/clients/client_factory.py`.

**Adding a new model:** add a value to `LLMModel` and update `model_to_provider_map` in `yalc/common/schemas.py`.
