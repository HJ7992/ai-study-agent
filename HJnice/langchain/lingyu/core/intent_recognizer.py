import json
import re
from dataclasses import dataclass
from typing import Any

from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .prompt import INTENT_RECOGNIZE_PROMPT


@dataclass
class IntentResult:
    intents:list[str]
    slots:dict[str, Any]
    confidence:float

## 意图识别
class IntentRecognizer:
    def __init__(self,llm:ChatTongyi):
        # chain = prompt | model | parser
        self.__prompt = ChatPromptTemplate.from_messages([
            ("system",INTENT_RECOGNIZE_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human","{input}")
        ])
        self.llm = llm
        self.chain = self.__prompt | self.llm |StrOutputParser()

    def recognize(self,user_input:str,chat_history:list[BaseMessage] | None = None)->IntentResult:
        chat_history = chat_history if chat_history else []
        result = self.chain.invoke({
            "chat_history":chat_history,
            "input":user_input
        })
        ## 解析大模型输出
        data = self.__parse_str_to_json(result)
        intents = data["intents"]
        if not isinstance(intents, list):
            intent = data.get("intent")
            intents = [intent] if isinstance(intent, str) else []
        slots = data.get("slots") if isinstance(data.get("slots"), dict) else {}
        try:
            confidence = float(data.get("confidence"))
        except ValueError:
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))

        return IntentResult(intents=intents,slots=slots,confidence=confidence)

    def __parse_str_to_json(self, result:str)->dict[str, Any]:
        if not result or not result.strip():
            return {"intents":[""],"slots":{},"confidence":0.0}
        ##尝试将str转为json
        text = result.strip()
        try:
            return json.loads(text)
        except json.decoder.JSONDecodeError:
            pass

        find_text = re.search(r"{{.*?}}", text,re.DOTALL)
        if find_text:
            try:
                return json.loads(find_text.group(0))
            except json.decoder.JSONDecodeError:
                pass

