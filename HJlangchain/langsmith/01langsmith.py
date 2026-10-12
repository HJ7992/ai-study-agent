import os
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()
from langchain_openai import ChatOpenAI

# 第1步：设置 API Key
# 去 https://smith.langchain.com/settings 注册并获取你的 Key
# 从 .env 或环境变量读取，避免将 Key 硬编码到代码里
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")

# 第2步：开启追踪开关
# 设为 "true" 表示开始记录；设为 "false" 可以随时关闭
os.environ["LANGSMITH_TRACING"] = "true"

# 第3步：指定项目名称
# 同一个项目的所有 Trace 会自动归到一起，方便管理
os.environ["LANGSMITH_PROJECT"] = "langsmith"

@traceable(run_type="llm")
def ask_(question : str) -> str:
    llm = ChatOpenAI(model="deepseek-v4.1-flash",
                     api_key=os.getenv("FZ_API_KEY"),
                     base_url=os.getenv("FZ_BASE_URL"))
    response = llm.invoke(question)
    return response.content
result = ask_("请用一句话解释什么是 LangSmith")
print(f"回答：{result}")