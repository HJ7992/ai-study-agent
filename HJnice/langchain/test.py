from langchain_community.chat_models import ChatTongyi
from langchain_community.llms.tongyi import Tongyi
import os
import dotenv
dotenv.load_dotenv()

llm = Tongyi(model="qwen-max",api_key=os.getenv("dashscope_API_KEY"))
# reply = llm.invoke("你好，你是什么模型")
# print(reply)
#流式输出
reply = llm.stream("模仿鲁迅写一首青年阶段迷茫，不知道做什么为主题的文字，300字左右")

for chunk  in  reply:
    print(chunk, end="",flush=True)