import os
import sys
import uuid

from dotenv import load_dotenv

# 直接运行本脚本时，把项目根目录加入 sys.path，否则无法导入 chat_servers 等顶层模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat_servers import ChatServers
from core.protocol import ChatRequest

load_dotenv()

# Windows 控制台默认 GBK 编码，无法输出 AI 回复中的 emoji（如 😊），统一切换为 UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

user_id = "test_user"

# 多轮对话列表
conversations = [
    "我的订单什么时候发货？",
    "ORD123456789",
    "能改地址吗？",
    "北京市朝阳区xxx",
    "谢谢",
    "没有了",
    "拜拜"
]
session_id = str(uuid.uuid4())
chat_service = ChatServers()
# 执行多轮对话
for round_num, user_input in enumerate(conversations, 1):
    request = ChatRequest(
        user_id=user_id,
        chat_session_id=session_id,  # 使用相同的 session_id
        trace_id=str(uuid.uuid4()),
        user_input=user_input,
        api_key=os.getenv("DASHSCOPE_API_KEY")
    )

    print(f"第{round_num}轮 - 用户: {user_input}")
    result = chat_service.handle(request)
    print(f"AI: {result.response}\n")