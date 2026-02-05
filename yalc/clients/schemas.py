from pydantic import BaseModel

from yalc.common.schemas import ContextMessage, LLMRole, ResponseStats


class ClientMessage(BaseModel):
    response: BaseModel
    role: LLMRole


class ClientCall(ResponseStats):
    context_messages: list[ContextMessage]
    client_message: ClientMessage
    model_name: str
