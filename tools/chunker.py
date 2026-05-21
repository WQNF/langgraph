# tools/chunker.py
import re
from typing import List

SEPARATORS = ["\n\n", "\n", "。", "！", "？", ".", ";", " ","；"]

def semantic_chunk_text(text: str, chunk_size: int = 100, overlap: int = 10) -> List[str]:
    """
    基于分隔符的递归分块，保持语义完整性。
    chunk_size: 期望的最大块字符数（大致，实际块可能略大于此值）
    overlap: 相邻块之间的重叠字符数
    """
    # 先按分隔符递归切分，得到基本段落
    segments = _split_by_separators(text, SEPARATORS)
    
    # 然后合并小的段落，形成接近 chunk_size 的块，并添加重叠
    chunks = []
    current_chunk = ""
    for seg in segments:
        if current_chunk and len(current_chunk) + len(seg) > chunk_size:
            # 当前块接近目标长度，保存
            chunks.append(current_chunk.strip())
            # 准备下一块，并加入重叠：取当前块最后 overlap 个字符（尽量在分隔符处截断）
            if overlap > 0 and len(current_chunk) > overlap:
                # 从 current_chunk 末尾向前寻找合适的分隔位置，避免从字符中间截断
                overlap_text = _cut_at_word_boundary(current_chunk, overlap)
                current_chunk = overlap_text + seg
            else:
                current_chunk = seg
        else:
            if current_chunk:
                current_chunk += " " + seg
            else:
                current_chunk = seg
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def _split_by_separators(text: str, separators: List[str]) -> List[str]:
    """递归使用分隔符分割文本，返回段落列表"""
    if not separators:
        return [text]
    
    sep = separators[0]
    if sep == "":
        # 单字符分割
        parts = list(text)
    elif re.escape(sep) != sep:
        # 正则转义处理
        parts = re.split(f"({re.escape(sep)})", text)
        # 把分隔符附加到前一个片段上（保留分隔符）
        merged = []
        for i, part in enumerate(parts):
            if i % 2 == 1 and i > 0:
                merged[-1] += part
            else:
                merged.append(part)
        parts = merged
    else:
        # 普通字符串分隔
        parts = text.split(sep)
        # 保留分隔符（附加到上一段）
        for i in range(len(parts)-1):
            parts[i] += sep
        # 移除末尾可能多出的空字符串
        parts = [p for p in parts if p]
    
    # 对每个部分继续用下一个分隔符递归切分
    next_seps = separators[1:]
    results = []
    for part in parts:
        if len(part) > max(200, text.count(sep)):  # 如果仍然很长，继续切分
            results.extend(_split_by_separators(part, next_seps))
        else:
            results.append(part)
    return results

def _cut_at_word_boundary(text: str, overlap: int) -> str:
    """从文本末尾往回截取约 overlap 长度的字符串，尽量在标点或空格处截断，避免单词/短语被撕开"""
    if overlap <= 0:
        return ""
    start_pos = max(0, len(text) - overlap)
    # 从 start_pos 向后找到第一个分隔符（。！？ ；\n等）
    for i in range(start_pos, len(text)):
        if text[i] in "。！？\n；; ":
            return text[i+1:]  # 从该分隔符之后开始
    return text[start_pos:]  # 没有合适分隔符，直接截取