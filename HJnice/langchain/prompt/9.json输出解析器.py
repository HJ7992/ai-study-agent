# 1.生成推荐电影的prompt（输出是JSON格式）*
import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate
load_dotenv()

prompt1 = PromptTemplate.from_template(
    "根据用户喜欢的电影类型，推荐一部电影并以JSON格式输出。\n"
    "用户类型：{genre}\n"
    "输出格式：{{\"title\": \"电影名称\", \"director\": \"导演\", \"year\": 上映年份, \"reason\": \"推荐理由\"}}"
)

# 2.创建模型客户端
model = ChatTongyi(model="qwen3-max",api_key=os.getenv("dashscope_API_KEY"),streaming=True)

# 3.创建json输出解析器
json_parser = JsonOutputParser()

# 4.拼接为chain格式
chain_1 = prompt1 | model | json_parser

# 5.调用chain & 输出结果


prompt2 = PromptTemplate.from_template( "请将以下电影推荐信息翻译成英文，只输出翻译结果。\n"
    "电影名称：{title}\n导演：{director}\n上映年份：{year}\n推荐理由：{reason}")

str_parser = StrOutputParser()

chain = chain_1 | prompt2 | model | str_parser

result = chain.stream(input={"genre":"科幻"})

for chunk in result:
    print(chunk)