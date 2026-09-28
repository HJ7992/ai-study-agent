import os

from langchain_community.vectorstores import Chroma

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(BASE_DIR, "chromaDBhj")
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

embeddings = OpenAIEmbeddings(
    model="doubao-embedding-vision",
    api_key=os.getenv("FZ_API_KEY"),
    base_url=os.getenv("FZ_BASE_URL"),
    check_embedding_ctx_length=False
)

def embed(data:list[Document])->str:
    vectorstore = Chroma(
        collection_name="HJ_collection",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )
    ids = vectorstore.add_documents(data)
    return ids