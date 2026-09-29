

from langchain_community.vectorstores import Chroma
from embed_and_storage import embedding_function

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
query = "什么是LangChain？"
relevant_docs = retriever_create().invoke(query)
print(f"检索到 {len(relevant_docs)} 个相关文档:")
for i, doc in enumerate(relevant_docs):
    print(f"\n--- 文档 {i+1} ---")
    print(doc.page_content)
    print(f"元数据: {doc.metadata}")