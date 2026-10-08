
from typing import Any
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .prompt import INTENT_RECOGNIZE_PROMPT

from pydantic import BaseModel,Field
from .prompt import INTENT_RECOGNIZE_PROMPT

class IntentResult(BaseModel):
    intents:list[str] = Field(description="意图列表，每一个元素为一个意图名称")
    slots:dict[str, Any] = Field(description="slots值字典，键为slots名称，值为slots值")
    confidence:float=Field(description="置信度分数，取值范围0-1，越大表示越确信该意图")


## 意图识别
class IntentRecognizer:
    def __init__(self,llm:ChatTongyi):
        # chain = prompt | model | parser
        self.__prompt = ChatPromptTemplate.from_messages([
            ("system",INTENT_RECOGNIZE_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human","{input}")
        ])
        self.llm = llm.with_structured_output(IntentResult)
        self.chain = self.__prompt | self.llm

    def recognize(self,user_input:str,chat_history:list[BaseMessage] | None = None)->IntentResult:
        chat_history = chat_history if chat_history else []
        result = self.chain.invoke({
            "chat_history":chat_history,
            "input":user_input
        })
        if result is None:
            print("结构化输出为None")
            return IntentResult(intents=["general"],slots={},confidence=0.0)
        return result




