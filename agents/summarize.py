# agents/summarize.py

from langchain_core.messages import HumanMessage, AIMessage
from core.llm import llm
from config.prompts import (
    INTENT_DETECTION_PROMPT,
    ATTRIBUTE_COMBO_ANALYSIS_PROMPT
)
from core.metrics import record_llm_usage
from skills.registry import get_skill
import re
from langgraph.config import get_stream_writer 

def _extract_pokemon_info(state: dict) -> tuple:
    """从状态消息中提取精灵名称、主属性、副属性、种族值总和"""
    pokemon_name = "该精灵"
    primary = ""
    secondary = ""
    species_total = "未提供"
    messages = state.get("messages", [])
    for msg in messages:
        if hasattr(msg, 'content') and '[Pokemon Agent]' in str(msg.content):
            content = str(msg.content)
            name_match = re.search(r"name\s*[=:]?\s*'?([^\s',]+)'?", content)
            if name_match:
                pokemon_name = name_match.group(1)
            primary_match = re.search(r"primary_type\s*[=:]?\s*'?([^\s',]+)'?", content)
            if primary_match:
                primary = primary_match.group(1)
            sec_match = re.search(r"secondary_type\s*[=:]?\s*'?([^\s',]+)'?", content)
            if sec_match:
                secondary = sec_match.group(1)
            total_match = re.search(r"species_total\s*[=:]?\s*(\d+)", content)
            if total_match:
                species_total = total_match.group(1)
    return pokemon_name, primary, secondary, species_total

def summarize_agent(state: dict) -> dict:
    writer = get_stream_writer()
    print("[Summarize Agent] 正在整合结果...")
    # 获取 writer 函数

    
    # 获取用户输入
    user_input = state.get("user_input", "")
    if not user_input and state.get("messages"):
        last_msg = state["messages"][-1]
        user_input = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
    if not user_input:
        user_input = "请提供帮助"

    # 收集所有专家的结果
    messages = state.get("messages", [])
    results = []

    # 1. 优先插入预加载的精灵数据（结构化）
    preloaded_pokemons = state.get("preloaded_pokemons", [])
    if preloaded_pokemons:
        poke_lines = ["【预加载精灵数据】"]
        for poke in preloaded_pokemons:
            line = (f"名称: {poke['name']} (No.{poke['national_number']}), "
                    f"属性: {poke['primary_type']}")
            if poke.get('secondary_type'):
                line += f" + {poke['secondary_type']}"
            line += f", 特性: {poke['ability']}, 种族值和: {poke['species_total']}"
            if poke.get('stats'):
                s = poke['stats']
                line += f"，生命: {s['hp']}，物攻: {s['attack']}，魔攻: {s['sp_attack']}，物防: {s['defense']}，魔防: {s['sp_defense']}，速度: {s['speed']}"
            poke_lines.append(line)
        results.insert(0, "\n".join(poke_lines))

    # 2. 插入预加载的属性克制信息
    preloaded_elements = state.get("preloaded_elements", [])
    if preloaded_elements:
        elem_text = "【预加载属性克制信息】\n" + "\n---\n".join(preloaded_elements)
        results.insert(0, elem_text)
    
    # 3. 插入预加载的团队数据
    preloaded_team = state.get("preloaded_team", [])
    if preloaded_team:
        team_lines = ["【预加载团队数据】"]
        for poke in preloaded_team:
            stats_str = ""
            if poke.get('stats'):
                s = poke['stats']
                stats_str = f" HP:{s['hp']} 物攻:{s['attack']} 魔攻:{s['sp_attack']} 物防:{s['defense']} 魔防:{s['sp_defense']} 速度:{s['speed']}"
            line = f"{poke['name']} 属性:{poke['primary_type']}"
            if poke.get('secondary_type'):
                line += f"+{poke['secondary_type']}"
            line += f", 特性:{poke.get('ability','')}, 种族和:{poke.get('species_total','')}{stats_str}"
            team_lines.append(line)
        results.insert(0, "\n".join(team_lines))
    
    # 4. 普通消息结果收集
    for msg in messages:
        if hasattr(msg, 'content') and '[Pokemon Agent]' in str(msg.content):
            results.append(f"精灵数据查询结果: {msg.content}")
        elif hasattr(msg, 'content') and '[RAG Agent]' in str(msg.content):
            results.append(f"知识库查询结果: {msg.content}")

    # 5. 如果消息中没有，从状态字段获取
    if not any("精灵数据查询结果" in r for r in results) and state.get("sql_result"):
        results.append(f"精灵数据查询结果: {state['sql_result']}")
    if not any("知识库查询结果" in r for r in results) and state.get("context_docs"):
        docs = state["context_docs"]
        results.append(f"知识库查询结果: " + "\n".join(docs[:5]))

    # 6. 如果仍然无结果，构建回顾性上下文
    need_agents = state.get("need_agents", [])
    if not results:
        if not need_agents:
            dialogue_summary = []
            recent = messages[-6:]
            for msg in recent:
                if isinstance(msg, HumanMessage):
                    dialogue_summary.append(f"用户: {msg.content[:150]}")
                elif isinstance(msg, AIMessage):
                    content = str(msg.content)
                    if any(tag in content for tag in [
                        "[Planner]", "[Dispatcher]", "已分析", "调用",
                        "已进入节点", "正在执行", "正在检索", "正在查询", "正在整合",
                        "未找到", "未获得有效回答", "暂无查询结果"
                    ]):
                        continue
                    dialogue_summary.append(f"助手: {content[:150]}")
            if dialogue_summary:
                results.append("【最近对话记录】\n" + "\n".join(dialogue_summary))
            else:
                results.append("暂无对话历史。")

    context = "\n".join(results) if results else "暂无查询结果"

    # 早期对话摘要
    compressed = state.get("compressed_context", "")
    if compressed:
        context = f"【早期重要对话摘要】\n{compressed}\n\n【当前查询结果】\n{context}"

    # 强制预加载数据优先提示
    priority_note = ""
    if state.get("preloaded_pokemons") or state.get("preloaded_elements") or state.get("preloaded_team"):
        priority_note = (
            "【重要指令】用户已通过前端预加载了部分数据（精灵、属性克制信息或队伍数据），这些数据已包含在【查询结果】中。"
            "请直接基于这些预加载信息进行分析，**不要使用其他可能冲突的知识**。如果预加载信息中已经包含完整的克制关系，"
            "则无需再依赖其他片段。\n\n"
        )

    # 技能优先
    active_skill = state.get("active_skill", "")
    skill_prompt = None
    if active_skill:
        skill = get_skill(active_skill)
        if skill:
            skill_prompt = skill.get_prompt()
            print(f"[Summarize Agent] 使用技能: {skill.name}")

    if skill_prompt:
        prompt = f"{skill_prompt}\n\n{priority_note}查询结果：\n{context}\n\n用户问题：{user_input}"
    else:
        # 意图检测（保持同步，不影响流式）
        intent_prompt = INTENT_DETECTION_PROMPT.format(user_input=user_input)
        intent_response =llm.invoke(intent_prompt)   # 改为异步 invoke
        record_llm_usage(intent_response, agent="summarize_intent")
        intent = intent_response.content.strip().lower()
        print(f"[Summarize Agent] 意图识别结果: {intent}")

        if intent == "analysis":
            pokemon_name, primary, secondary, species_total = _extract_pokemon_info(state)
            if primary:
                secondary_info = f" + {secondary}" if secondary else "（单属性）"
                prompt = ATTRIBUTE_COMBO_ANALYSIS_PROMPT.format(
                    pokemon_name=pokemon_name,
                    primary_type=primary,
                    secondary_type_info=secondary_info,
                    secondary_type=secondary if secondary else "",
                    context=f"{priority_note}{context}"
                )
            else:
                prompt = f"""你是智能的精灵对战助手。请严格基于以下查询结果回答用户问题。
{priority_note}
【查询结果】
{context}
用户问题：{user_input}
请整合信息回答，不要添加外部知识。"""
        else:
            prompt = f"""你是洛克王国的智能精灵助手，可以查询精灵数据库、分析属性克制关系、评估队伍联防、计算伤害、提供培养建议，并记住对话历史。请严格基于以下【查询结果】来回答用户问题。
【查询结果】中可能包含多段文档，你需要将它们整合成一个连贯的答案。克制关系的分析请严格按照游戏规则进行。

【最基础规则】
- 只能使用查询结果中明确出现的信息，不得添加任何你自己的知识或猜测。
- 如果查询结果中没有相关信息，请直接说明“未找到相关信息”。

【游戏规则】
1. 属性克制关系解读：
   - “克制”：指该属性攻击对手时会造成2倍伤害。
   - “抵抗”：指该属性受到对应属性攻击时受到的伤害降低至0.5倍。
   - “被克制”：指该属性受到对应属性攻击时伤害为正常伤害的2倍。
   - “被抵抗/抵抗”：指对手属性抵抗该属性的技能攻击。
   - “强力克制”：指某种属性技能攻击时，同时克制敌方两种属性。如【水系】技能攻击【火系+机械系】双属性精灵，由于水系克制火系，同时也克制机械系，因此属于强力克制，造成3倍伤害
   - “强力抵抗”：指某种属性技能攻击时，同时抵抗敌方两种属性。如【水系】技能攻击【草系+电系】双属性精灵，由于草系抵抗水系，同时电系也抵抗草系，因此属于强力抵抗，造成1/3倍伤害

{priority_note}
【查询结果】
{context}

用户问题：{user_input}

请严格按照上述规则，整合以上信息并专业地回答用户问题："""

    # ---- 异步流式生成回答 ----
    print("[Summarize Agent] 开始异步流式生成回答...")
    full_response = ""
    for chunk in llm.stream(prompt):
        token = chunk.content
        if token:
            full_response += token
            # 通过 writer 发送 token
            writer({"token": token})   # 注意：官方示例发送的是 dict
        print(token, end="", flush=True)
            # 这里不需要手动发送事件，LangGraph 的 astream_events 会自动捕获
    print("[Summarize Agent] 整合完成")


    return {
        "messages": [AIMessage(content=full_response)],
        "task_completed": True,
        "step_count": state.get("step_count", 0) + 1,
        "compressed_context": state.get("compressed_context", ""),
        "preloaded_pokemons": preloaded_pokemons,
        "preloaded_elements": preloaded_elements,
        "preloaded_team": preloaded_team,
    }