from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage

##全局存储
_session_store : dict[str,BaseChatMessageHistory] = {}

class ChatHistoryManager:
    def __init__(self,chat_session_id:str) -> None:
        self.chat_session_id = chat_session_id

    def get_history_object(self) -> BaseChatMessageHistory:
        """获取对应会话id的存储对象"""
        if self.chat_session_id not in _session_store:
            _session_store[self.chat_session_id] = InMemoryChatMessageHistory()
        return _session_store[self.chat_session_id]

    def get_messages(self)->list[BaseMessage]:
        """获取会话列表的所有消息"""
        return self.get_history_object().messages

    def add_user_message(self,content:str)->None:
        """add user message"""
        self.get_history_object().add_user_message(content)

    def add_ai_message(self, content: str) -> None:
        """添加AI消息"""
        self.get_history_object().add_ai_message(content)

    def get_recent_messages(self,count:int)->list[BaseMessage]:
        """get recent messages"""
        messages = self.get_messages()
        return messages[-count:] if  messages else []

    def clear(self)->None:
        """clear  messages"""
        self.get_history_object().clear()