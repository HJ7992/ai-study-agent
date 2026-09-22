## 1. 导入调用模型的统一封装包，多轮对话使用聊天模型
from langchain_community.chat_models import ChatTongyi
import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage

load_dotenv()
class multiTurnChat:
    def __init__(self,sys_prompt,model):
        self.llm = ChatTongyi(
            model=model,
            api_key=os.getenv("dashscope_API_KEY"),
            streaming=True
        )
        self.history = []
        if sys_prompt:
            self.history.append(('system',sys_prompt))

    def add_user_msg(self,msg_user):
        if msg_user:
            self.history.append(('user',msg_user))


    def add_ai_msg(self,msg_ai):
            self.history.append(('ai',msg_ai))


    def send(self,msg_user):
        self.add_user_msg(msg_user)
        reply = self.llm.stream(self.history)
        reply_ai=''
        for msg in reply:
            if msg.content:
                reply_ai += msg.content
                yield msg.content
        self.history.append(('ai',reply_ai))

if __name__ == '__main__':
    ss = multiTurnChat("你现在是一位专业的ai老师，请站在你的角度回答我的问题","qwen3-max")
    chunks = ss.send("rag的实现流程是什么")
    for chunk in chunks:
        if chunk:
            print(chunk)

