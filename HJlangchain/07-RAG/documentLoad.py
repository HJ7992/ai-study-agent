
import os

from langchain_community.document_loaders import DirectoryLoader, TextLoader, WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 以当前文件所在目录为基准，避免受运行时工作目录影响
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def loads_txt()->list[Document]:
    loder = DirectoryLoader(
        DATA_DIR,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    return loder.load()

def load_web(url:str)->list[Document]:
    loader = WebBaseLoader(url)
    return loader.load()


##递归字符串切块
def recursive_spliter(data:list[Document])->list[Document]:
    spliter = RecursiveCharacterTextSplitter(
        chunk_size=50,
        chunk_overlap=10,
        separators=["\n\n", "\n", "。", "，", " ", ""],
    )
    return spliter.split_documents(data)
