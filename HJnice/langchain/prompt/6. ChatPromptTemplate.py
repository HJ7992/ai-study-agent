#1. 准备提示词模板
import os
from dotenv import load_dotenv
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

load_dotenv()
chat_prompt_template = ChatPromptTemplate.from_messages([
    ("system", "假设你是一个{expert}专家"),
    ("human", "什么是{user_input}")]
)
llm = ChatTongyi(model="qwen-max",api_key=os.getenv("dashscope_API_KEY"),streaming=True)

chain = chat_prompt_template | llm

result = chain.stream(input={"expert": "AI", "user_input": "Langgraph"})

for chunk in result:
    print(chunk.content,end='',flush=True)