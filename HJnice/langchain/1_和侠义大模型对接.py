from langchain_community.llms.tongyi import Tongyi

# 1. 创建客户端
llm = Tongyi(model="qwen-max",api_key="")
llm.invoke("")
