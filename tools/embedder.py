import os
from typing import List
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

#Embedding_model =os.getenv("EMBEDDING_MODEL")
#API_KEY = os.getenv("SILICONFLOW_API_KEY")
#API_BASE = os.getenv("SILICONFLOW_API_BASE")

embedding_model = OpenAIEmbeddings(
    model="Qwen/Qwen3-Embedding-0.6B",
    api_key="sk-ajmudvyymtslxolpirzmjppmqhlgvxzqvshygkzhcqxilqih", 
    base_url="https://api.siliconflow.cn/v1"
)

def embed_texts(texts: List[str]) -> List[List[float]]:
    """将文本列表转换为 embedding 向量列表"""
    return embedding_model.embed_documents(texts)

def embed_query(text: str) -> List[float]:
    """将查询文本转换为 embedding 向量"""
    return embedding_model.embed_query(text)