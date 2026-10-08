import os
import sys
from pathlib import Path

# 将 lingyu 模块根目录加入 sys.path（保证直接从终端运行脚本时也能 import core）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage

from core.env_loader import load_env
from core.intent_recognizer import IntentRecognizer

# 统一加载环境变量（向上查找 ai-agent 主项目的 .env）
load_env()

if __name__ == "__main__":
    llm = ChatTongyi(
        model="qwen3-max",
        api_key=os.getenv("dashscope_API_KEY"),
    )
    recognizer = IntentRecognizer(llm)
    result = recognizer.recognize("我的订单号是11223344",[HumanMessage("我想退货")])
    print(result)