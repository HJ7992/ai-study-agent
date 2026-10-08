#1. 准备提示词模板
import os
from dotenv import load_dotenv
from langchain_community.llms.tongyi import Tongyi
from langchain_core.prompts import PromptTemplate

load_dotenv()
prompt_template = PromptTemplate.from_template(
    """假设你是一个{expert}专家，请你解释一下{content}是什么。"""
)

##2. 创建客户端
llm = Tongyi(model="qwen-max",api_key=os.getenv("dashscope_API_KEY"))

#3. LCEL
chain = prompt_template | llm
# 4. 调用

reply = chain.stream(input={"expert": "AI", "content": "Langgraph"})
for chunk in reply:
    print(chunk)