import os

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

def embedding_function():
    embeddings = OpenAIEmbeddings(
        model="doubao-embedding-vision",
        api_key=os.getenv("FZ_API_KEY"),
        base_url=os.getenv("FZ_BASE_URL"),
        check_embedding_ctx_length=False
    )
    return embeddings

def embed(data:list[Document])-> list[str]:
    vectorstore = Chroma(
        collection_name="HJ_collection",
        embedding_function=embedding_function(),
        persist_directory="chromaDBhj"
    )
    ids = vectorstore.add_documents(data)
    return ids