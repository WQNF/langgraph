"""
统一检索模块：支持 Milvus 向量库检索
可扩展为 Faiss 兼容接口（通过环境变量切换）
"""
import os
from typing import List, Optional, Tuple
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
from langchain_core.documents import Document


class BaseRetriever:
    """检索器抽象基类，方便以后切换 Faiss/Milvus"""
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Document, float]]:
        raise NotImplementedError


class MilvusRetriever(BaseRetriever):
    """Milvus 向量检索器"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 19530,
        collection_name: str = "knowledge_base",
        dim: int = 1024,
    ):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.dim = dim
        
        # 连接 Milvus
        connections.connect(host=self.host, port=self.port)
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self) -> Collection:
        """获取或创建 Collection（如果不存在）"""
        if utility.has_collection(self.collection_name):
            return Collection(self.collection_name)
        
        # 定义字段
        id_field = FieldSchema(
            name="id",
            dtype=DataType.INT64,
            is_primary=True,
            auto_id=True
        )
        embedding_field = FieldSchema(
            name="embedding",
            dtype=DataType.FLOAT_VECTOR,
            dim=self.dim
        )
        text_field = FieldSchema(
            name="text",
            dtype=DataType.VARCHAR,
            max_length=65535
        )
        
        schema = CollectionSchema(
            fields=[id_field, embedding_field, text_field],
            description="OmniPilot 知识库"
        )
        
        collection = Collection(self.collection_name, schema)
        
        # 创建索引（IVF_FLAT 适合小规模数据）
        index_params = {
            "metric_type": "IP",  # 内积相似度（如果用归一化向量，等价于余弦相似度）
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index("embedding", index_params)
        
        return collection
    
    def insert(self, texts: List[str], embeddings: List[List[float]]):
        """批量插入文本和向量"""
        entities = [
            {"text": text, "embedding": emb}
            for text, emb in zip(texts, embeddings)
        ]
        self.collection.insert(entities)
        self.collection.flush()
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Tuple[Document, float]]:
        """
        搜索向量库
        :param query_embedding: 查询的 embedding 向量
        :param top_k: 返回 top_k 个最相似文档
        :param score_threshold: 相似度阈值，低于此值的文档将被过滤
        :return: List of (Document, score)
        """
        self.collection.load()
        search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["text"]
        )
        
        docs_with_scores = []
        if results and results[0]:
            for hits in results[0]:
                score = hits.score
                if score_threshold is not None and score < score_threshold:
                    continue
                doc = Document(page_content=hits.entity.get("text", ""))
                docs_with_scores.append((doc, score))
        
        return docs_with_scores
    
    def retrieve(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Document]:
        """仅返回文档列表（不带分数）"""
        results = self.search(query_embedding, top_k, score_threshold)
        return [doc for doc, _ in results]


# ========== 工厂函数：根据环境变量选择检索器 ==========
def get_retriever(
    backend: Optional[str] = None,
    **kwargs
) -> BaseRetriever:
    """
    获取检索器实例
    :param backend: "milvus" 或 "faiss"，如果为 None 则从环境变量 RETRIEVER_BACKEND 读取
    """
    if backend is None:
        backend = os.getenv("RETRIEVER_BACKEND", "milvus")
    
    if backend.lower() == "milvus":
        return MilvusRetriever(**kwargs)
    else:
        raise ValueError(f"不支持的检索后端: {backend}")