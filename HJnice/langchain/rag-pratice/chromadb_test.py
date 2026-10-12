from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

embed_model = OpenAIEmbeddings(
    model="text-embedding-v4",
    api_key="sk-ws-H.PHRREIE.jQD0.MEQCIDb8Tv2MBL35Zv157S8tFb0hY5KPnfBsNFdXt0KjbGAcAiAvlHAit_YklHYS-XQmG30u3UyLjt2sIUEZh23VlCYF5Q",
    base_url="https://maas.qianwenaiapi.com/compatible-mode/v1",
    check_embedding_ctx_length=False,
)
chroma = Chroma(
    collection_name="sample_collection",
    embedding_function=embed_model,
    persist_directory="./chromadb",
    collection_metadata={"hnsw:space": "cosine"}
)
user_query = "如何学习人工智能？"
documents = [
        "学习AI需要先掌握线性代数、概率论和微积分，这是算法的基础",
        "如何做红烧肉，需要准备五花肉、冰糖和生抽",
        "Python是AI开发的首选语言，需要熟悉numpy、pandas等数据处理库",
        "通过Kaggle竞赛实战，从泰坦尼克号预测等项目开始练手",
        "人工智能的核心数学知识包括矩阵运算、概率统计和导数计算",
        "推荐李飞飞的CS231n课程和《深度学习》花书，系统学习理论"
    ]
data = [Document(page_content=doc) for doc in documents]
chroma.add_documents(
        documents=data,
        ids=[f"id-{i}" for i in range(len(data))]
    )


result = chroma.max_marginal_relevance_search( # #MMR最大边界相关性      搜索
    query=user_query,
    k=3,
    fetch_k=5,##候选池
    lambda_mult=0.6##平衡参数 【0，1】越大相关性越高，多样性越低
)
for i, doc in enumerate(result):
        print(f"排名{i + 1}: 内容: {doc.page_content[:40]}...")

