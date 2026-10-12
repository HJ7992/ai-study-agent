import logging
import os
import time

from langchain_community.chat_models import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from config import INTENT_RECOGNIZER_MODEL, DASHSCOPE_MODEL
from core.intent_recognizer_with_strutured_output import IntentRecognizer
from core.memory import Memory
from core.protocol import ChatRequest, ChatResponse

log = logging.getLogger(__name__)

RECENT_MESSAGES_COUNT = 6
CONFIDENCE_THRESHOLD = 0.3
def _handle_low_confidence(
) ->str:
    return """
    抱歉没能理解您的需求。请问您是想：\n
    1. 查询物流进度\n
    2. 修改退货地址\n
    3. 申请退货退款\n
    4. 投诉建议\n
    请回复数字或需求。
    """
def _system_prompt_by_intent(intent: str) -> str:
    mapping = {
        "track_shipping": "你是电商物流查询客服。先要订单号/运单号；如果缺失就追问。",
        "change_address": "你是电商改地址客服。先确认是否已发货；需要订单号+新地址。",
        "refund": "你是电商退货退款客服。先给3步结论，再给注意事项，最后引导用户提供订单号。",
        "complaint": "你是电商投诉处理客服。先安抚，再收集订单号与问题细节，给出处理时效。",
        "general": "你是一个友好、简洁的聊天助手。",
    }
    return mapping.get(intent.strip(), mapping["general"])

class ChatServers:
    def __init__(self,api_key : str | None = None) -> None:
        if api_key:
            os.environ["DASHSCOPE_API_KEY"] = api_key
        if not os.environ.get("DASHSCOPE_API_KEY"):
            raise KeyError("DASHSCOPE_API_KEY not set")
        self.__intent_recognizer = IntentRecognizer(ChatTongyi(
            model=INTENT_RECOGNIZER_MODEL,
        ))
        self.__memory_cache :dict[str,Memory] = {}
        self.__llm = ChatTongyi(
            model=DASHSCOPE_MODEL,
        )

    def _get_memory(self,chat_session_id : str) ->Memory:
        if chat_session_id not in self.__memory_cache:
            self.__memory_cache[chat_session_id] = Memory(chat_session_id)
        return self.__memory_cache[chat_session_id]

    def handle(self,request : ChatRequest) -> ChatResponse:
        chat_session_id = request.chat_session_id
        memory = self._get_memory(chat_session_id)
        start = time.perf_counter()
        try:
            # 1. 意图识别
            intent_result = self.__intent_recognizer.recognize(
                request.user_input,
                memory.get_recent_n_messages(RECENT_MESSAGES_COUNT)
            )
            # 2. 低置信度
            if intent_result.confidence <= CONFIDENCE_THRESHOLD:
                low_conf = _handle_low_confidence()
                return ChatResponse(
                    user_id=request.user_id,
                    chat_session_id=chat_session_id,
                    trace_id=request.trace_id,
                    response = low_conf
                )
            # 3. 确定主要意图，路由到对应链路（目前只做单意图）
            intents = intent_result.intents
            primary_intent = intents[0] if intents else "general"

            # 4. 构建不同提示词
            prompt =ChatPromptTemplate.from_messages([
                ("system",_system_prompt_by_intent(primary_intent)),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])

            # 5. 记忆管理
            messages = memory.prepare_memory_for_llm()

            # 6.调用大模型
            chain = prompt | self.__llm | StrOutputParser()
            response = chain.invoke({"chat_history":messages,"input":request.user_input})

            # 7. 写回消息历史
            memory.add_user_message(message=request.user_input,llm=self.__llm)
            memory.add_ai_message(message=response,llm=self.__llm)

            # 8. 更新【事实】
            memory.update_key_facts(intent_result.slots)

            # 9. 日志记录
            self.__log(
                req=request,
                intents=intents,
                confidence=intent_result.confidence,
                action="handle",
                latency_ms=int((time.perf_counter() - start) * 1000),
            )

            return ChatResponse(
                user_id=request.user_id,
                chat_session_id=chat_session_id,
                trace_id=request.trace_id,
                response=response
            )

        except Exception as e:
            # 异常也记录到日志
            self.__log(
                req=request,
                intents=[],
                confidence=0.0,
                action="handle",
                latency_ms=int((time.perf_counter() - start) * 1000),
                error=str(e),
            )
            return ChatResponse(
                user_id=request.user_id,
                chat_session_id=chat_session_id,
                trace_id=request.trace_id,
                response="抱歉，系统暂时开小差了，请稍后再试。",
            )

    def __log(self,
              *,
              req: ChatRequest,
              intents: list[str],
              confidence: float,
              action: str,
              latency_ms: int,
              error: str | None = None):
        payload = {
            "trace_id": req.trace_id,
            "user_id": req.user_id,
            "session_id": req.chat_session_id,
            "intents": intents,
            "confidence": confidence,
            "action": action,
            "latency_ms": latency_ms
        }
        # 如果有错误信息，记录为错误日志error，否则记录为普通日志info
        if error:
            payload["error"] = error
            log.error(payload)
        else:
            log.info(payload)
