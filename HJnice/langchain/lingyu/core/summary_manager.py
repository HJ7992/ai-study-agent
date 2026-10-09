from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import BaseMessage, HumanMessage, ChatMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from core.prompt import SUMMARY_GENERATION_PROMPT

## 摘要存储
_summary_store : dict[str,str] = {}

##未摘要的消息数量
_unsummarized_count : dict[str,int] = {}

#默认配置
SUMMARY_BATCH_SIZE = 12

str_output_parser = StrOutputParser()


class SummaryManager:
    def __init__(self,chat_session_id)->None:
        self.chat_session_id = chat_session_id
        if self.chat_session_id not in _summary_store:
            _summary_store[self.chat_session_id] = ""
        if self.chat_session_id not in _unsummarized_count:
            _unsummarized_count[self.chat_session_id] = 0

    def get_summary(self)->str:
        """获取当前会话摘要"""
        return _summary_store.get(self.chat_session_id,"")

    def update_summary(self,new_summary : str)->None:
        """更新摘要"""
        _summary_store[self.chat_session_id] = new_summary

    def get_unsummarized_summary_count(self)->int:
        """获取未摘要的消息数量"""
        return _unsummarized_count.get(self.chat_session_id,0)

    def increment_summary_count(self,delta:int = 1)->None:
        """计数器"""
        current = _unsummarized_count.get(self.chat_session_id,0)
        _unsummarized_count[self.chat_session_id] = current + delta

    def reset_summary_count(self)->None:
        """重置计数"""
        _unsummarized_count[self.chat_session_id] = 0

    def should_trigger_summary(self,)->bool:
        """是否达到阈值"""
        return _unsummarized_count[self.chat_session_id] >= SUMMARY_BATCH_SIZE

    def generate_increment_summary(
            self,
            old_summary:str,
            new_messages:list[BaseMessage],
            llm:ChatTongyi | None
                                   )->str:
        if not new_messages:
            return old_summary

        messages_text = ""

        for message in new_messages:
            if isinstance(message,HumanMessage):
                messages_text += f"human: {message.content}\n"
            elif isinstance(message,AIMessage):
                messages_text += f"ai: {message.content}\n"

        ##调用模型生成摘要
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system",SUMMARY_GENERATION_PROMPT),
                ("human",f"旧摘要{old_summary}，新消息：{messages_text}"),
            ])

            chain = prompt | llm | StrOutputParser()

            result = chain.invoke({})
            new_summary = result.strip()
            return new_summary
        except :
            return self._simple_summary(old_summary,messages_text)

    def _simple_summary(self,old_summary:str,messages_text:str)->str:
        if old_summary and old_summary != "[摘要]：无":
            old_part = old_summary[:150] if len(old_summary) >= 150 else old_summary
            new_part = messages_text[:150] if len(messages_text) >= 150 else messages_text
            return f"摘要 ： {old_part}...{new_part}"
        else:
            new_part = messages_text[:150] if len(messages_text) >= 150 else messages_text
            return "[摘要] ：{new_part} "
