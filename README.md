# Yet Another LLM Client

An opinionated python wrapper for LLM calls. Supports multiple LLM providers:

- OpenAI
- Anthropic
- more to come...

Uses [pydantic](https://docs.pydantic.dev/latest/) models to serialize LLM responses. Every response **has** to be serialized into a pydantic model.

Full async support.

## Usage

Every call to the LLM returns some metadata. Metadata contains token usage, costs, model used and context messages. YALC supports 2 modes of operations for handling metadata.

### Metadata return mode

Metadata is returned directly alongside the response as a tuple.

```python
client = create_client(LLMModel.gpt_4o_mini)

result, metadata = await client.structured_response(
    JudgmentResult, messages
)
```

Advantages:

- Simple, no setup required
- Direct access to metadata at the call site

Disadvantages:

- Must handle metadata manually on every call
- Easy to forget or handle inconsistently across call sites

### Strategy metadata mode

A metadata handler strategy is provided during client creation. The strategy is automatically invoked on every call when a `context` is passed. The provided `context` is used for any additional data that needs to be used when handling LLM call metadata.

```python
# 1. Define your strategy
class LogStrategy(ClientMetadataStrategy[LLMLogContext]):
    def handle(self, call: ClientCall, context: LLMLogContext):
        print(f"Tokens: {call.input_tokens + call.output_tokens}")
        print(f"Cost: {call.input_tokens_cost + call.output_tokens_cost}")
        db.save(call.model_dump(), context.request_id)

# 2. Create client with the strategy
client = create_client(LLMModel.gpt_4o_mini, metadata_strategies=[LogStrategy()])

# 3. Pass context to trigger the strategy
result = await client.structured_response(
    JudgmentResult, messages, context=llm_log_context
)
```

Advantages:

- Metadata handling is set up once and applied consistently
- Call sites stay clean — no need to unpack or handle metadata each time

Disadvantages:

- More initial setup
- Metadata handling is implicit, which can be harder to trace
