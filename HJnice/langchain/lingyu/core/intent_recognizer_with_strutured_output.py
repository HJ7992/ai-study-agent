
import logging
from typing import Any
from langchain_community.chat_models import ChatTongyi
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .prompt import INTENT_RECOGNIZE_PROMPT

from pydantic import BaseModel,Field

log = logging.getLogger(__name__)

##意图识别，使用Pydantic结构化输出

class IntentResult(BaseModel):
    intents:list[str] = Field(description="意图列表，每一个元素为一个意图名称")
    slots:dict[str, Any] = Field(description="slots值字典，键为slots名称，值为slots值")##插槽
    confidence:float=Field(description="置信度分数，取值范围0-1，越大表示越确信该意图")


## 意图识别
class IntentRecognizer:
    def __init__(self,llm:BaseChatModel):
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
        invoke_kwargs = {
            "chat_history":chat_history,
            "input":user_input
        }
        # 结构化输出解析失败时 with_structured_output 会返回 None，重试一次
        result = self.chain.invoke(invoke_kwargs)
        if result is None:
            log.warning("intent recognize returned None, retrying...")
            result = self.chain.invoke(invoke_kwargs)
        if result is None:
            # 重试仍失败，返回低置信度默认结果，走兜底引导话术
            log.warning("intent recognize failed after retry, fallback to low-confidence result")
            return IntentResult(intents=["general"], slots={}, confidence=0.0)
        return result




