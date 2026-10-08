from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv
load_dotenv()
#1. 创建模型客户端

llm = ChatTongyi(model="qwen3-max",
                 api_key=os.getenv("dashscope_API_KEY"),
                 streaming=True,)

chat_history = [
    ("system",'你现在是一位专业的ai老师，请站在你的角度回答我的问题'),
    ("user",'rag的实现流程是什么')
    # SystemMessage(content="你现在是一位专业的ai老师，请站在你的角度回答我的问题"),
    # HumanMessage(content="rag的实现流程是什么")
]
# reply = llm.invoke(input=chat_history)
# print(type(reply))
# print(reply.content)
reply = llm.stream(chat_history)
for message in reply:
    print(message.content)## 流式输出
