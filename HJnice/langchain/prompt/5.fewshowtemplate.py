import os
from sys import prefix

from dotenv import load_dotenv
from langchain_community.llms.tongyi import Tongyi
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from spacy.lang.en.tokenizer_exceptions import word

load_dotenv()

##1 . 示例
examples = [{"input": "高兴", "output": "愉悦"},
    {"input": "快速", "output": "迅猛"},
    {"input": "美丽", "output": "绚丽"}]
##2. 基础模板
example_prompt = PromptTemplate.from_template(template="输入：{input}\n输出：{output}")

##3. 创建FewShowPromptTemplate
few_show_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix='请根据以下示例，将输入词语转换为同义词',
    suffix='基于示例回答问题。用户输入：{word}\n输出：',
    input_variables=["word"]
)
## prompt_text = few_show_prompt.format(word="悲伤")
##4 .创建客户端
llm = Tongyi(model="qwen-max",api_key=os.getenv("dashscope_API_KEY"))

chain = few_show_prompt | llm

reply = chain.invoke(word="悲伤")
print(reply)
