

from langgraph.store.memory import InMemoryStore
from langgraph.store.base import IndexConfig  # 可选：向量搜索配置
from langchain_openai import OpenAIEmbeddings
##from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()
##embeddings = HuggingFaceEmbeddings(model_name=r"D:\example\python\rag-demo\day2\bge-large-zh-v1.5")
embeddings = OpenAIEmbeddings(model="doubao-embedding-vision",
                              openai_api_base=os.getenv("FZ_BASE_URL"),
                              openai_api_key=os.getenv("FZ_API_KEY"),
                              check_embedding_ctx_length=False)

store = InMemoryStore(
    index = IndexConfig(
        embed=lambda text:embeddings.embed_documents(list(text)),
        dims=1024
    )
)

store.put(
    ('users',),
    "HJnice",
    {"content":'用户喜欢简介的回答'}
)

result = store.search(("users",), query="用户偏好短回答")
print(result)