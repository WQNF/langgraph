# agents/planner.py
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from core.llm import llm
import json
import re
from config.prompts import PLANNER_PROMPT
from core.metrics import record_llm_usage
from core.memory import manage_memory

def planner_node(state: dict) -> dict:
    print("==================")
    print("已进入节点-planner")
    print("[Planner] 正在分析问题并生成计划...")

    # ---- 记忆修剪与压缩 ----
    messages = state.get("messages", [])
    pruned_msgs, compressed = manage_memory(messages, keep_turns=3)
    user_input = state.get("user_input", "")
    if not user_input and pruned_msgs:
        for msg in reversed(pruned_msgs):
            if isinstance(msg, HumanMessage):
                user_input = msg.content
                break

    # ---- 获取预加载数据 ----
    # 团队预加载优先
    preloaded_team = state.get("preloaded_team", [])
    if preloaded_team:
        print("[Planner] 检测到预加载队伍，启用团队分析规则")
        return {
            "need_agents": ["team_analyzer"],
            "active_skill": "team_synergy",
            "messages": [AIMessage(content="已分析，调用 team_analyzer")],
            "compressed_context": compressed,
            "recent_messages": pruned_msgs[-6:],
            "relation": "serial",
            "preloaded_pokemons": state.get("preloaded_pokemons", []),
            "preloaded_elements": state.get("preloaded_elements", []),
            "preloaded_team": preloaded_team,
        }
    preloaded_pokemons = state.get("preloaded_pokemons", [])
    preloaded_elements = state.get("preloaded_elements", [])


    # ---- 规则引擎：有预加载数据时，直接决定 need_agents ----
    if preloaded_pokemons or preloaded_elements:
        print("[Planner] 检测到预加载数据，启用规则引擎")

        need_agents = []
        active_skill = ""

        if preloaded_pokemons:
            # 预加载了精灵，需要查询属性克制关系
            need_agents.append("rag_agent")
            active_skill = "type_analysis"

        if preloaded_elements:
            # 预加载了属性，需要查询相同属性的精灵
            need_agents.append("pokemon_agent")
            # 如果还未设置技能（没有精灵预加载），则设为 pokemon_lookup
            if not active_skill:
                active_skill = "pokemon_lookup"

        # 如果两者都有，则同时保留两个 agent（后续 Dispatcher 可按需调度）
        # 如果都没有但进入了这个分支（理论上不会），则回退到 LLM 规划
        if not need_agents:
            print("[Planner] 预加载数据为空？回退到 LLM 规划")
            # 这里的回退逻辑可以保留原有 LLM 调用（略），为简洁我们直接返回空
            need_agents = []
            active_skill = ""

        print(f"[Planner] 规则引擎输出: need_agents={need_agents}, skill={active_skill}")

        return {
            "need_agents": need_agents,
            "active_skill": active_skill,
            "messages": [AIMessage(content=f"已分析，调用 {need_agents}，技能 {active_skill}")],
            "compressed_context": compressed,
            "recent_messages": pruned_msgs[-6:],
            "relation": "serial",  # 默认串行，避免并发冲突
            "preloaded_pokemons": preloaded_pokemons,   # 继续传递
            "preloaded_elements": preloaded_elements,
        }

    # ---- 无预加载数据时，使用 LLM 规划 ----
    recent_summary = ""
    for msg in pruned_msgs[-6:]:
        if isinstance(msg, HumanMessage):
            recent_summary += f"用户: {msg.content[:200]}\n"
        elif isinstance(msg, AIMessage):
            recent_summary += f"助手: {msg.content[:200]}\n"

    history_summary = ""
    if compressed:
        history_summary += f"早期重要对话摘要：\n{compressed}\n\n"
    history_summary += f"最近对话：\n{recent_summary}"

    prompt = PLANNER_PROMPT.format(
        user_input=user_input,
        history_summary=history_summary
    )
    response = llm.invoke(prompt)
    record_llm_usage(response, agent="planner")
    response_text = response.content.strip()

    # 解析 LLM 输出（与原有逻辑相同）
    need_agents = []
    active_skill = ""
    relation = "serial"
    try:
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        plan_data = json.loads(response_text)
        need_agents = plan_data.get("experts", [])
        active_skill = plan_data.get("skill", "")
        relation = plan_data.get("relation", "serial")
    except json.JSONDecodeError:
        matches = re.findall(r'\[(.*?)\]', response_text)
        if matches:
            experts_str = matches[-1].replace('"', '').replace("'", "").replace(' ', '')
            need_agents = [exp for exp in experts_str.split(',') if exp]
        else:
            if "rag_agent" in response_text.lower():
                need_agents.append("rag_agent")
            if "pokemon_agent" in response_text.lower():
                need_agents.append("pokemon_agent")
        if "team_synergy" in response_text.lower():
            active_skill = "team_synergy"
        elif "type_analysis" in response_text.lower():
            active_skill = "type_analysis"
        elif "pokemon_lookup" in response_text.lower():
            active_skill = "pokemon_lookup"

    print(f"[Planner] LLM 规划: experts={need_agents}, skill={active_skill}, relation={relation}")

    return {
        "need_agents": need_agents,
        "active_skill": active_skill,
        "messages": [AIMessage(content=f"已分析，调用 {need_agents}，技能 {active_skill}")],
        "compressed_context": compressed,
        "recent_messages": pruned_msgs[-6:],
        "relation": relation,
        "preloaded_pokemons": preloaded_pokemons,
        "preloaded_elements": preloaded_elements,
    }