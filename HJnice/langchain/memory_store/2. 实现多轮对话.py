import os
from typing import Dict, List

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

_session_store : Dict[str,BaseChatMessageHistory] = {}
load_dotenv()

##记忆类
class Memory:
    def get_message_history(self,chat_session_id:str) ->BaseChatMessageHistory:
        if chat_session_id not in _session_store:
            _session_store[chat_session_id] = InMemoryChatMessageHistory()
        return _session_store[chat_session_id]

    def add_human_message(self,chat_session_id:str,message:str | HumanMessage) ->None:
        history = self.get_message_history(chat_session_id)
        if isinstance(message,str):
            history.add_message(HumanMessage(message))
        else:
            history.add_message(message)

    def add_ai_message(self,chat_session_id:str,message:str | AIMessage) ->None:
        history = self.get_message_history(chat_session_id)
        if isinstance(message,str):
            history.add_message(AIMessage(message))
        else:
            history.add_message(message)

    def get_messages(self,chat_session_id:str) -> List[BaseMessage]:
        history = self.get_message_history(chat_session_id)
        return history.messages
##对话类

class ChatSession:
    def __init__(self,chat_session_id:str,system_prompt : str = "你是一个ai助手") -> None:
        self.prompt = ChatPromptTemplate.from_messages([
            ("system",system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human","{input}")
        ])
        self.chat_session_id = chat_session_id
        self.memory = Memory()
        self.model = ChatTongyi(
            model="qwen3-max",
            api_key=os.getenv("dashscope_API_KEY"),
            streaming=True,
        )
        self.parser = StrOutputParser()
        self.chain = self.prompt | self.model | self.parser

    def send(self,user_input):
        chat_history = self.memory.get_messages(self.chat_session_id)
        stream = self.chain.stream({
            "chat_history":chat_history,
            "input":user_input
        })

        full_reply = ''
        for chunk in stream:
            full_reply += chunk
            yield chunk
        self.memory.add_human_message(self.chat_session_id,user_input)
        self.memory.add_ai_message(self.chat_session_id,full_reply)

if __name__ == "__main__":
    session = ChatSession("chat_session_id1")

    print("用户: 你好，我叫阿苑")
    print("AI: ", end='', flush=True)
    for chunk in session.send("你好，我叫阿苑"):
        print(chunk, end='', flush=True)
    print()

    print("用户: 我叫什么名字？")
    print("AI: ", end='', flush=True)
    for chunk in session.send("我叫什么名字？"):
        print(chunk, end='', flush=True)
    print()