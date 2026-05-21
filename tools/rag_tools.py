# tools/rag_tools.py
"""从 Milvus 精确检索属性克制文档（复用 rag_agent 的核心逻辑）"""
import re
from typing import List
from tools.retriever import get_retriever
from tools.embedder import embed_query
from tools.reranker import call_siliconflow_rerank

VALID_ELEMENTS = [
    "火系", "水系", "草系", "光系", "恶系", "幽系",
    "普通系", "地系", "冰系", "龙系", "电系", "毒系",
    "虫系", "武系", "翼系", "萌系", "机械系", "幻系"
]

def retrieve_attribute_docs(attributes: List[str], user_query: str = "") -> List[str]:
    """
    根据属性列表，从 Milvus 中精确检索对应的克制文档。
    attributes: 可以是 ["光系"] 或 ["光系+草系", "草系+草系"]
    user_query: 用于向量检索的查询（可选）
    返回: 文档文本列表（去重）
    """
    print(f"\n【retrieve_attribute_docs】开始检索属性文档")
    print(f"  输入属性: {attributes}")
    print(f"  用户查询: {user_query if user_query else '属性克制'}")
    
    if not attributes:
        print("  属性列表为空，返回空列表")
        return []

    retriever = get_retriever()
    query_embedding = embed_query(user_query if user_query else "属性克制")
    candidate_docs = retriever.retrieve(query_embedding, top_k=172, score_threshold=0.0)
    print(f"  向量检索返回 {len(candidate_docs)} 个候选文档")
    
    if not candidate_docs:
        print("  未找到任何候选文档")
        return []

    docs_text = [doc.page_content for doc in candidate_docs]
    final_docs = []

    for attr in attributes:
        # 1. 精确匹配完整字符串（如【光系】、【光系+草系】）
        pattern = re.escape(f"【{attr}】")
        found = None
        for doc in docs_text:
            if re.search(pattern, doc):
                found = doc
                break

        # 2. 如果 attr 是单属性（如“光系”），也可能匹配到双属性文档中的一部分
        if not found and "+" not in attr:
            # 匹配以该属性开头的双属性：【光系+草系】
            for doc in docs_text:
                if re.search(rf"【{re.escape(attr)}\+", doc):
                    found = doc
                    break
            # 匹配以该属性结尾的双属性：【草系+光系】
            if not found:
                for doc in docs_text:
                    if re.search(rf"\+{re.escape(attr)}】", doc):
                        found = doc
                        break

        if found:
            final_docs.append(found)
            print(f"  属性【{attr}】匹配成功")
        else:
            print(f"  属性【{attr}】未找到匹配文档")
        # 注意：不再进行重排序兜底，避免耗时；如果找不到就跳过该属性

    print(f"【retrieve_attribute_docs】完成，返回 {len(final_docs)} 个文档")
    return list(set(final_docs))  # 去重