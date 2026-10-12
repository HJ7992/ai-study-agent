from dataclasses import dataclass


@dataclass(frozen=True)
class ChatRequest:
    api_key : str
    user_id : str
    chat_session_id : str
    user_input : str
    trace_id : str



@dataclass(frozen=True)
class ChatResponse:
    user_id: str
    chat_session_id: str
    trace_id: str
    response: str