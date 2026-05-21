import re
from langchain_core.messages import HumanMessage, AIMessage
from core.state import multiagentstate
from core.llm import llm
from tools.retriever import get_retriever
from tools.embedder import embed_query
from tools.reranker import call_siliconflow_rerank
from config.prompts import RAG_PROMPT, INTENT_ANALYSIS_PROMPT, VALID_ELEMENTS
from core.metrics import record_llm_usage
import json

def rag_agent(state: multiagentstate) -> dict:
    print("[RAG Agent] 正在执行智能属性检索...")

    user_input = state.get("user_input", "")
    if not user_input and state.get("messages"):
        last_msg = state["messages"][-1]
        user_input = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
    if not user_input:
        user_input = "请提供帮助"

    print(f"[RAG Agent] 原始用户输入: {user_input}")

    # ── 1. 属性嗅探（改进版：按精灵分别提取，避免错误合并）──
    search_patterns = []
    preloaded_pokemons = state.get("preloaded_pokemons", [])

    if preloaded_pokemons:
        # 为每只预加载的精灵生成各自的搜索模式
        for poke in preloaded_pokemons:
            primary = poke.get("primary_type")
            secondary = poke.get("secondary_type")
            if secondary and secondary in VALID_ELEMENTS:
                # 双属性精灵：生成双属性组合
                a, b = primary, secondary
                search_patterns.extend([f"【{a}+{b}】", f"【{b}+{a}】"])
            elif primary and primary in VALID_ELEMENTS:
                # 单属性精灵：生成单属性模式
                search_patterns.append(f"【{primary}】")
        # 去重（保持顺序）
        seen = set()
        unique_patterns = []
        for p in search_patterns:
            if p not in seen:
                seen.add(p)
                unique_patterns.append(p)
        search_patterns = unique_patterns
        print(f"[RAG Agent] 从预加载精灵生成搜索模式: {search_patterns}")

    if not search_patterns:
        # 没有预加载精灵或未提取到属性，尝试从消息历史嗅探（原有逻辑）
        sniffed_types = []
        messages = state.get("messages", [])
        for msg in reversed(messages[-10:]):
            content = ""
            if hasattr(msg, 'content'):
                content = str(msg.content)
            elif isinstance(msg, dict) and 'content' in msg:
                content = str(msg['content'])
            found = re.findall(r'属性:\s*(\S+系)', content)
            if not found:
                found = re.findall(r"'primary_type':\s*'(\S+系)'", content)
            for t in found:
                if t in VALID_ELEMENTS and t not in sniffed_types:
                    sniffed_types.append(t)
            if len(sniffed_types) >= 2:
                break
        if sniffed_types:
            print(f"[RAG Agent] 消息历史嗅探到属性: {sniffed_types}")
            if len(sniffed_types) == 1:
                search_patterns = [f"【{sniffed_types[0]}】"]
            else:
                a, b = sniffed_types[0], sniffed_types[1]
                search_patterns = [f"【{a}+{b}】", f"【{b}+{a}】"]
        else:
            # 使用 LLM 意图分析
            prompt = INTENT_ANALYSIS_PROMPT.format(
                valid_elements=", ".join(VALID_ELEMENTS),
                user_input=user_input
            )
            resp = llm.invoke(prompt)
            intent_json = resp.content.strip()
            try:
                if intent_json.startswith("```json"):
                    intent_json = intent_json[7:]
                if intent_json.endswith("```"):
                    intent_json = intent_json[:-3]
                intent_result = json.loads(intent_json)
            except Exception:
                intent_result = {"search_patterns": []}
            search_patterns = intent_result.get("search_patterns", [])
            print(f"[RAG Agent] LLM 意图分析结果: {intent_result}")

    print(f"[RAG Agent] 最终搜索模式: {search_patterns}")

    # ── 2. 检索与精确匹配 ──
    final_docs = []
    retriever = get_retriever()
    query_embedding = embed_query(user_input)
    candidate_docs = retriever.retrieve(query_embedding, top_k=172, score_threshold=0.0)

    if not candidate_docs:
        print("[RAG Agent] 无相关文档，回退到通用回答")
        response = llm.invoke(f"用户：{user_input}\n请直接回答：")
        answer = response.content
        record_llm_usage(response, agent="rag")
        return {
            "messages": [AIMessage(content=f"[RAG Agent] {answer}")],
            "context_docs": [],
            "executed_agents_history": state.get("executed_agents_history", []) + ["rag_agent"],
            "step_count": state.get("step_count", 0) + 1,
            "active_skill": state.get("active_skill", ""),
            "compressed_context": state.get("compressed_context", ""),
            "preloaded_pokemons": preloaded_pokemons,
            "preloaded_elements": state.get("preloaded_elements", []),
            "preloaded_team": state.get("preloaded_team", []),
        }

    docs_text = [doc.page_content for doc in candidate_docs]

    if search_patterns:
        # 精确正则匹配（每个模式独立匹配，收集所有命中）
        pattern_docs = []
        for pat in search_patterns:
            for doc in docs_text:
                if pat in doc:
                    pattern_docs.append(doc)
                    break   # 每个模式只取第一个匹配，避免过多重复
        if pattern_docs:
            final_docs = pattern_docs
            print(f"[RAG Agent] 正则精确匹配到 {len(final_docs)} 个文档")
        else:
            print("[RAG Agent] 精确匹配未命中，使用重排序模型")
            reranked = call_siliconflow_rerank(query=user_input, documents=docs_text, top_n=5)
            if reranked:
                indices = [item['index'] for item in reranked]
                final_docs = [docs_text[idx] for idx in indices if idx < len(docs_text)]
            else:
                final_docs = docs_text[:5]
    else:
        print("[RAG Agent] 无搜索模式，使用向量检索 + 重排序")
        reranked = call_siliconflow_rerank(query=user_input, documents=docs_text, top_n=5)
        if reranked:
            indices = [item['index'] for item in reranked]
            final_docs = [docs_text[idx] for idx in indices if idx < len(docs_text)]
        else:
            final_docs = docs_text[:5]

    # ── 3. 生成最终答案 ──
    if final_docs:
        context = "\n\n".join(final_docs)
        prompt = RAG_PROMPT.format(context=context, user_query=user_input)
        response = llm.invoke(prompt)
        answer = response.content.strip()
        record_llm_usage(response, agent="rag")
    else:
        answer = "未在知识库中找到相关属性克制信息。"

    executed_agents = state.get("executed_agents_history", [])
    if "rag_agent" not in [agent['name'] if isinstance(agent, dict) else agent for agent in executed_agents]:
        executed_agents.append("rag_agent")

    return {
        "messages": [AIMessage(content=f"[RAG Agent] {answer}")],
        "context_docs": final_docs,
        "executed_agents_history": executed_agents,
        "step_count": state.get("step_count", 0) + 1,
        "active_skill": state.get("active_skill", ""),
        "compressed_context": state.get("compressed_context", ""),
        "preloaded_pokemons": preloaded_pokemons,
        "preloaded_elements": state.get("preloaded_elements", []),
        "preloaded_team": state.get("preloaded_team", []),
    }