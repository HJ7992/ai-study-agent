import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
load_dotenv()
prompt = PromptTemplate.from_template(
    "请解释一下{word}的概念"
)
llm = ChatTongyi(model="qwen-max",api_key=os.getenv("dashscope_API_KEY"),streaming=True)

chain = prompt|llm|StrOutputParser()

reply  = chain.stream(input={"word":"langchain"})

for chunk  in reply:
    print(chunk)