from pathlib import Path

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from config.setting import QaConfig


class VectorManager:
    def __init__(self,config:QaConfig):
        self.__config = config
        self.__embeddings = DashScopeEmbeddings(
            model=config.embedding_model
        )


    def load_or_build(self,filehash:str,chunks:list[Document]) -> Chroma:
        if not filehash:
            raise ValueError("文件哈希不能为空")
        chroma = Chroma(
            persist_directory=str(self.get_persist_dir(filehash)),
            collection_name=self.get_collection_name(filehash),
            embedding_function=self.__embeddings,
            collection_metadata={"hnsw:space":"cosine"}
        )
        ##存在数据则直接返回
        if chroma._collection.count()>0:
            return chroma
        else:
            if not chunks:
                raise ValueError("未提供chunks,无法建库")
            try:
                chroma.add_documents(chunks,ids=[f"idx{idx}" for idx in range(len(chunks))])
            except Exception as e:
                raise e
            return chroma


    def get_persist_dir(self,filehash:str) -> Path:
        return Path(self.__config.chroma_root_dir)/f"pdf_{filehash}"
    def get_collection_name(self,filehash:str) -> str:
        return self.__config.collection_prefix+f"{filehash}"
