# core/memory.py
from typing import List, Tuple
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from core.llm import llm
import json

# 权重评估提示词
WEIGHT_EVAL_PROMPT = """你是一个对话重要性评估器。请为下面这一轮对话（用户提问+助手回答）的重要性打分（0.0 ~ 1.0）。 
评分标准：
- 包含具体数据（种族值、技能伤害、属性克制关系）→ 0.8~1.0
- 包含精灵分析、队伍配备建议 → 0.6~0.8
- 简单闲聊、功能询问、回顾性问题 → 0.0~0.3
- 其他一般问题 → 0.3~0.6

只返回一个 JSON 格式：{{"score": 0.75}}

对话轮次：
用户：{user_msg}
助手：{assistant_msg}
"""

def manage_memory(messages: List[BaseMessage], keep_turns: int = 3) -> Tuple[List[BaseMessage], str]:
    """
    管理记忆，返回修剪后的消息列表（最近 keep_turns 轮）和压缩摘要。
    一轮 = 一次用户提问 + 对应助手回答（可能有多条消息，简单取连续的人类和AI消息）。
    """
    # 1. 将消息整理为轮次列表
    turns = []  # 每个元素：{"user": msg, "assistants": [msg, ...]}
    current_turn = {"user": None, "assistants": []}
    for msg in messages:
        if isinstance(msg, HumanMessage):
            if current_turn["user"] is not None:  # 新的一轮
                turns.append(current_turn)
                current_turn = {"user": None, "assistants": []}
            current_turn["user"] = msg
        elif isinstance(msg, AIMessage):
            current_turn["assistants"].append(msg)
    if current_turn["user"] is not None:
        turns.append(current_turn)

    # 2. 划分最近 keep_turns 轮和更早的轮次
    if len(turns) <= keep_turns:
        # 无需压缩，直接返回全部消息和空摘要
        return messages, ""

    recent_turns = turns[-keep_turns:]
    older_turns = turns[:-keep_turns]

    # 3. 对更早的轮次评估权重，保留高权重者并进行摘要
    important_summaries = []
    for turn in older_turns:
        user_content = turn["user"].content if turn["user"] else ""
        assistant_content = " ".join([m.content for m in turn["assistants"] if hasattr(m, 'content')])
        # 调用 LLM 评估权重
        prompt = WEIGHT_EVAL_PROMPT.format(user_msg=user_content[:500], assistant_msg=assistant_content[:500])
        try:
            resp = llm.invoke(prompt)
            result = json.loads(resp.content)
            score = result.get("score", 0.5)
        except:
            score = 0.5

        # 如果权重大于0.6，则生成摘要（或者只保留用户原话+助手要点）
        if score >= 0.6:
            # 用LLM生成简短摘要
            summary_prompt = f"请将以下对话轮次总结为一条简短摘要（不超过50字），用于记忆上下文：\n用户：{user_content}\n助手：{assistant_content}\n摘要："
            summ_resp = llm.invoke(summary_prompt)
            summary = summ_resp.content.strip()
            important_summaries.append(f"[历史重要对话] {summary}")

    # 4. 重建修剪后的消息列表（只保留最近 keep_turns 轮）
    pruned_messages = []
    for turn in recent_turns:
        pruned_messages.append(turn["user"])
        for a in turn["assistants"]:
            pruned_messages.append(a)

    # 5. 生成压缩摘要字符串
    compressed = "\n".join(important_summaries) if important_summaries else ""

    return pruned_messages, compressed