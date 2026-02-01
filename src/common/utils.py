from src.common.schemas import ContextMessage, LLMRole


def to_context_messages(messages: list[dict]) -> list[ContextMessage]:
    return [
        ContextMessage(message=m["content"], role=LLMRole(m["role"]))
        for m in messages
    ]
