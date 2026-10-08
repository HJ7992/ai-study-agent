
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
import os
from embed_and_storage import embedding_function
from dotenv import load_dotenv
load_dotenv()

model = ChatOpenAI(
        model="kimi-k2.7-code",
        api_key=os.getenv("FZ_API_KEY"),
        base_url=os.getenv("FZ_BASE_URL")
)
def retriever_create():
    vectorstore = Chroma(
        collection_name="HJ_collection",
        embedding_function=embedding_function(),
        persist_directory="chromaDBhj"
    )
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 2},
    )
    return retriever
#带相关性评分的检索
# results_with_score = vectorstore.similarity_search_with_score(query, k=3)
# for doc, score in results_with_score:
#     print(f"评分: {score:.4f} | 内容: {doc.page_content[:80]}...")

# 测试检索
# query = "什么是LangChain？"
# relevant_docs = retriever_create().invoke(query)
# print(f"检索到 {len(relevant_docs)} 个相关文档:")
# for i, doc in enumerate(relevant_docs):
#     print(f"\n--- 文档 {i+1} ---")
#     print(doc.page_content)
#     print(f"元数据: {doc.metadata}")

def rag_answer(question:str,retriever):
    relevant_docs = retriever.invoke(question)
    if not relevant_docs:
        return "未检索到信息"
        # 构建上下文
    context = "\n\n".join([
        f"[来源: {doc.metadata.get('source', 'unknown')}] {doc.page_content}"
        for doc in relevant_docs
    ])
    # 构建提示词
    prompt = f"""你是一个知识问答助手。请基于以下提供的参考信息回答用户的问题。

    参考信息：
    {context}

    如果参考信息中没有相关内容，请明确告知用户。不要编造信息。

    用户问题：{question}

    请给出简洁、准确的回答："""
    response = model.invoke([{"role": "user", "content": prompt}])
    return response.content

if __name__ == "__main__":
    retriever_create()