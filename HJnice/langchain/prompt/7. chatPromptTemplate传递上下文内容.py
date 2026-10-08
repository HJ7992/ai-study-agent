#1. 准备提示词模板
import os
from dotenv import load_dotenv
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder

load_dotenv()
chat_prompt_template = ChatPromptTemplate.from_messages([
    ("system", "假设你是一个ai专家"),
    MessagesPlaceholder("history"),
    ("human", "我刚才问了什么内容")]
)

chat_history = [("human", "什么是Langgraph"),
    ("ai", "LangGraph是一种将自然语言处理（NLP）与图神经网络（GNN, Graph Neural Networks）相结合的技术或方法。")]

## prompt_text = chat_prompt_template.format(history=chat_history)
## prompt_text = chat_prompt_template.invoke(input={"history":chat_history})

llm = ChatTongyi(model="qwen-max",api_key=os.getenv("dashscope_API_KEY"),streaming=True)

chain = chat_prompt_template | llm

result = chain.stream(input={"history":chat_history})

for chunk in result:
    print(chunk.content,end='',flush=True)