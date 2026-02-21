from pydantic import BaseModel

from yalc.common.schemas import ContextMessage, LLMRole, ResponseStats


class ClientMessage(BaseModel):
    """The parsed response message returned by an LLM, together with its role."""

    response: BaseModel
    role: LLMRole


class ClientCall(ResponseStats):
    """Full record of a single LLM call: input messages, parsed response, and token/cost stats."""

    context_messages: list[ContextMessage]
    client_message: ClientMessage
    model_name: str
