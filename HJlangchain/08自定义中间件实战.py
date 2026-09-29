from langchain.agents.middleware import wrap_tool_call, before_model, after_model, wrap_model_call, ModelRequest, \
    ModelResponse
import time


@wrap_tool_call
def retry_middleware(request,handler):
    """为Tool调用添加重试机制，最多重试3次。

        Args:
            request: Tool调用请求对象，包含 tool_call 信息
            handler: 实际的Tool执行函数
        """
    max_retries = 3
    tool_name= request.tool_call['name']
    for attempt in range(max_retries):
        try:
            return handler(request)
        except Exception as e:
            print(f"Tool '{tool_name}' 调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt + 1 == max_retries:
                raise
            time.sleep(2**attempt)

@before_model
def log_before_model(state,runtime):
    """记录每次模型调用前的日志。"""
    msg_count = len(state["messages"])
    last_msg = state["messages"][-1].content if state["messages"] else ""
    print(f"[{time.strftime('%H:%M:%S')}] 调用模型 | 历史消息数: {msg_count} | 最新输入: {last_msg[:50]}...")


@after_model
def log_after_model(state, runtime):
    """记录模型调用后的日志。"""
    last_ai_msg = None
    for msg in reversed(state["messages"]):
        if hasattr(msg, 'content') and hasattr(msg, 'type') and msg.type == 'ai':
            last_ai_msg = msg
            break
    if last_ai_msg:
        content_preview = last_ai_msg.content[:50] if last_ai_msg.content else ""
        print(f"[{time.strftime('%H:%M:%S')}] 模型响应完成 | 输出: {content_preview}...")

@wrap_tool_call
def log_tool_call(request, handler):
    """记录Tool调用的耗时和结果。"""
    tool_name = request.tool_call["name"]
    tool_args = request.tool_call.get("args", {})
    start = time.time()

    try:
        result = handler(request)
        elapsed = time.time() - start
        log_entry = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "tool": tool_name,
            "args": tool_args,
            "result": str(result)[:100],
            "elapsed_seconds": round(elapsed, 3),
            "status": "success"
        }
        print(f"[{log_entry['timestamp']}] Tool '{tool_name}' 执行成功 | 耗时: {elapsed:.2f}s")
        return result
    except Exception as e:
        elapsed = time.time() - start
        log_entry = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "tool": tool_name,
            "args": tool_args,
            "error": str(e),
            "elapsed_seconds": round(elapsed, 3),
            "status": "error"
        }
        print(f"[{log_entry['timestamp']}] Tool '{tool_name}' 执行失败 | 耗时: {elapsed:.2f}s | 错误: {e}")
        raise



@wrap_tool_call
def dangerous_tool_guard(request, handler):
    """拦截已禁用的危险Tool调用。

    Args:
        request: Tool调用请求对象
        handler: 实际的Tool执行函数
    """
    blocked_tools = ["delete_database", "format_disk", "execute_shell"]
    tool_name = request.tool_call["name"]

    if tool_name in blocked_tools:
        return f"错误: Tool '{tool_name}' 已被管理员禁用，请联系系统管理员"

    return handler(request)



from pydantic import BaseModel, Field
from typing import Callable

class SimpleResponse(BaseModel):
    """简短回答（对话初期）。"""
    answer: str = Field(description="简短回答")

class DetailedResponse(BaseModel):
    """详细回答（对话深入后）。"""
    answer: str = Field(description="详细回答")
    reasoning: str = Field(description="推理过程")
    confidence: float = Field(description="置信度 0-1")

@wrap_model_call
def state_based_output(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """根据消息数量动态选择输出格式。"""
    message_count = len(request.messages)

    if message_count < 3:
        # 对话初期：使用简单格式
        request = request.override(response_format=SimpleResponse)
    else:
        # 对话深入后：使用详细格式
        request = request.override(response_format=DetailedResponse)

    return handler(request)


