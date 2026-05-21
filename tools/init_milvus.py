import os
import sys
import re  # 新增，用于正则拆分
from dotenv import load_dotenv

# 将项目根目录添加到Python路径中
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
doc_dir = os.path.join(BASE_DIR, "data", "documents")

from tools.retriever import MilvusRetriever
from tools.embedder import embed_texts
from pymilvus import utility, connections
from tools.chunker import semantic_chunk_text

load_dotenv()

# ========== 单属性专用拆分 ==========
def split_single_type(text: str) -> list[str]:
    parts = re.split(r'(\d+、)', text)
    chunks = []
    current_chunk = ""
    for part in parts:
        if re.match(r'\d+、', part):
            if current_chunk.strip():
                # 提取属性名称（如"火系"），先去掉编号
                first_line = current_chunk.split('\n')[0]
                clean_first = re.sub(r'^\d+、', '', first_line)
                # 直接捕获属性名（例如“火系”）
                element_match = re.search(r'(\S+系)', clean_first)
                if element_match:
                    element = element_match.group(1)
                    # 将内容的第一行也替换成干净的形式，保持整体整洁
                    current_chunk_lines = current_chunk.split('\n')
                    current_chunk_lines[0] = clean_first.strip()
                    chunk_body = '\n'.join(current_chunk_lines).strip()
                    current_chunk = f"【{element}】\n{chunk_body}"
                chunks.append(current_chunk.strip())
            current_chunk = part
        else:
            current_chunk += part
    if current_chunk.strip():
        first_line = current_chunk.split('\n')[0]
        clean_first = re.sub(r'^\d+、', '', first_line)
        element_match = re.search(r'(\S+系)', clean_first)
        if element_match:
            element = element_match.group(1)
            current_chunk_lines = current_chunk.split('\n')
            current_chunk_lines[0] = clean_first.strip()
            chunk_body = '\n'.join(current_chunk_lines).strip()
            current_chunk = f"【{element}】\n{chunk_body}"
        chunks.append(current_chunk.strip())
    return chunks

# ========== 双属性专用拆分 ==========
def split_dual_type(text: str) -> list[str]:
    parts = re.split(r'(\d+、)', text)
    chunks = []
    current_chunk = ""
    for part in parts:
        if re.match(r'\d+、', part):
            if current_chunk.strip():
                # 提取属性组合，去掉编号
                first_line = current_chunk.split('\n')[0]
                clean_first = re.sub(r'^\d+、', '', first_line)
                combo_match = re.search(r'(\S+系\+\S+系)', clean_first)
                if combo_match:
                    combo = combo_match.group(1)  # 例如 "机械系+幻系"
                    # 将内容第一行也更新为不带编号的
                    current_chunk_lines = current_chunk.split('\n')
                    current_chunk_lines[0] = clean_first.strip()
                    chunk_body = '\n'.join(current_chunk_lines).strip()
                    current_chunk = f"【{combo}】\n{chunk_body}"
                chunks.append(current_chunk.strip())
            current_chunk = part
        else:
            current_chunk += part
    if current_chunk.strip():
        first_line = current_chunk.split('\n')[0]
        clean_first = re.sub(r'^\d+、', '', first_line)
        combo_match = re.search(r'(\S+系\+\S+系)', clean_first)
        if combo_match:
            combo = combo_match.group(1)
            current_chunk_lines = current_chunk.split('\n')
            current_chunk_lines[0] = clean_first.strip()
            chunk_body = '\n'.join(current_chunk_lines).strip()
            current_chunk = f"【{combo}】\n{chunk_body}"
        chunks.append(current_chunk.strip())
    return chunks

# ========== 流式分块工具（避免内存溢出） ==========
def chunk_file(filepath: str, chunk_size: int = 500, overlap: int = 100):
    """
    流式读取文件并分块（自动适应多种编码）
    """
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                chunk = f.read(chunk_size)
                while chunk:
                    yield chunk
                    current_pos = f.tell()
                    if len(chunk) < chunk_size:
                        break
                    next_start = current_pos - overlap
                    f.seek(next_start)
                    chunk = f.read(chunk_size)
            return
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"无法读取文件 {filepath} （尝试了 utf-8, gbk, gb2312, latin-1）")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    """原有的内存分块函数，保留备用（用于小文本）"""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

# ========== 初始化主函数 ==========
def init_knowledge_base(doc_dir: str = doc_dir):
    # 1. 连接并清理旧集合
    connections.connect(host="localhost", port="19530")
    if utility.has_collection("knowledge_base"):
        utility.drop_collection("knowledge_base")
    retriever = MilvusRetriever()

    all_chunks = []
    for filename in os.listdir(doc_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(doc_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()

            if filename == "单属性克制表.txt":
                chunks = split_single_type(text)
                for i, chunk in enumerate(chunks):
                    tagged_chunk = f"[Source: {filename} | Chunk {i+1}]\n{chunk}"
                    all_chunks.append(tagged_chunk)
            elif filename == "双属性克制表.txt":
                chunks = split_dual_type(text)
                for i, chunk in enumerate(chunks):
                    tagged_chunk = f"[Source: {filename} | Chunk {i+1}]\n{chunk}"
                    all_chunks.append(tagged_chunk)
            else:
                # 其他文档继续用语义分块
                chunks = semantic_chunk_text(text, chunk_size=100, overlap=10)
                for i, chunk in enumerate(chunks):
                    tagged_chunk = f"[Source: {filename} | Chunk {i+1}]\n{chunk}"
                    all_chunks.append(tagged_chunk)

    if not all_chunks:
        print("❌ 未找到文档")
        return

    print(f"📊 共计 {len(all_chunks)} 个块，开始嵌入...")
    embeddings = embed_texts(all_chunks)
    retriever.insert(all_chunks, embeddings)
    print(f"🎉 知识库初始化完成！存入 {len(all_chunks)} 个块。")

if __name__ == "__main__":
    init_knowledge_base()