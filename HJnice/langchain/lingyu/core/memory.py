from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, ToolMessage

from core.chat_history_manager import ChatHistoryManager
from core.facts_manager import FactsManager
from core.intent_recognizer_with_strutured_output import IntentRecognizer
from core.summary_manager import SummaryManager

SESSION_KEY = "session"
class Memory:
    """记忆管理整合三个独立管理器，1. 意图识别 intent_recognize_with_struct_output
        2. 摘要 summary_manager 3. 关键事实存储 facts_manager"""
    def __init__(self,chat_session_id):
        self.chat_session_id = chat_session_id
        self.session_key = f"{SESSION_KEY}:{self.chat_session_id}"
        ##初始化三个管理器
        self.history = ChatHistoryManager(self.session_key)
        self.summary_manager = SummaryManager(self.session_key)
        self.facts_manager = FactsManager(self.session_key)

    ##====对话历史相关=====
    def get_session_history(self) ->BaseChatMessageHistory:
        """获取消息历史"""
        return self.history.get_history_object()

    def get_session_messages(self) ->list[BaseMessage]:
        """获取列表"""
        return self.history.get_messages()

    def get_recent_n_messages(self,recent_n : int) -> list[BaseMessage]:
        """获取最近n条信息"""
        return self.history.get_recent_messages(recent_n)

    def get_recent_n_messages_text(self,recent_n : int) ->str:
        """获取文本"""
        messages = self.get_recent_n_messages(recent_n)
        message_text = ""
        for message in messages:
            if isinstance(message,AIMessage):
                message_text += f"ai:{message.content}"
            elif isinstance(message,HumanMessage):
                message_text += f"human:{message.content}"
            elif isinstance(message,ToolMessage):
                message_text += f"tool:{message.content}"
        return message_text

    ##============ 添加消息==============
    def add_user_message(self,message : str,llm : BaseChatModel) -> None:
        self.history.add_user_message(message)
        self.summary_manager.increment_summary_count()
        ###判断是否需要摘要更新
        self._trim_and_summarized(llm)

    def add_ai_message(self,message : str,llm : BaseChatModel) -> None:
        self.history.add_ai_message(message)
        self.summary_manager.increment_summary_count()
        ###判断是否需要摘要更新
        self._trim_and_summarized(llm)

    ##===========事实相关===============

    def get_key_facts(self) ->dict[str,str]:
        """获取全部关键事实"""
        return self.facts_manager.get_all_facts()

    def update_key_facts(self,new_facts : dict[str,str]) -> None:
        """更新"""
        self.facts_manager.update_fact(new_facts)

    def clear_facts(self) -> None:
        self.facts_manager.clear_facts()

    ##===========摘要相关===========
    def _trim_and_summarized(self,llm):    ##判断是否达到摘要阈值
        if not self.summary_manager.should_trigger_summary():
            return

        history = self.history.get_history_object()
        if not history.messages:
            return

        messages = self.history.get_messages()
        unsummarized_count = self.summary_manager.get_unsummarized_summary_count()

        ##获取未摘要的消息/新消息
        un_summarized_messages = messages[-unsummarized_count:]
        if un_summarized_messages:
            old_summary = self.summary_manager.get_summary()
            new_summary = self.summary_manager.generate_increment_summary(
                old_summary,
                un_summarized_messages,
                llm,
            )
            self.summary_manager.update_summary(new_summary)
            self.summary_manager.reset_summary_count()

        # ============准备上下文================
    def prepare_memory_for_llm(self) ->list[BaseMessage]:
        result = []
        #添加关键事实
        facts = self.get_key_facts()
        if facts:
            facts_text = "|".join([f"{k}:{v}" for k,v in facts.items()])
            result.append(AIMessage(f"关键事实：{facts_text}"))

        #添加摘要
        summary = self.summary_manager.get_summary()
        if summary:
            result.append(AIMessage(f"摘要：{summary}"))

        #添加未被摘要的消息历史
        unsummarized_count = self.summary_manager.get_unsummarized_summary_count()
        if unsummarized_count:
            new_messages = self.history.get_messages()[-unsummarized_count:]
            result.extend(new_messages)

        return result





