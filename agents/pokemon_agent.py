# agents/pokemon_agent.py
from langchain_core.messages import HumanMessage, AIMessage
from config.prompts import SQL_GENERATION_PROMPT
from core.metrics import record_llm_usage
from core.llm import llm

def pokemon_agent(state: dict) -> dict:
    print("====================")
    print("已进入节点-Pokemon Agent")
    print("[Pokemon Agent] 正在查询精灵数据...")
    
    # 获取用户输入
    user_input = state.get("user_input", "")
    if not user_input and state.get("messages"):
        last_msg = state["messages"][-1]
        user_input = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
    if not user_input:
        user_input = "查询精灵数据"

    # ---- 优先使用预加载属性构建查询意图 ----
    preloaded_elements = state.get("preloaded_elements", [])
    if preloaded_elements:
        # 提取预加载的属性信息中的属性名称（从类似 "火系克制水系" 的文本中提取）
        # 简单做法：用正则提取所有出现的系别，去重
        import re
        elem_pattern = r'(火系|水系|草系|光系|恶系|幽系|普通系|地系|冰系|龙系|电系|毒系|虫系|武系|翼系|萌系|机械系|幻系)'
        found_elements = []
        for text in preloaded_elements:
            found = re.findall(elem_pattern, text)
            found_elements.extend(found)
        # 去重
        unique_elements = list(set(found_elements))
        if unique_elements:
            # 构造明确的查询提示，替换 user_input
            element_list = "、".join(unique_elements)
            user_input = f"请查询所有主属性或副属性包含 {element_list} 的精灵，列出它们的名称、编号、属性、种族值和特性。"
            print(f"[Pokemon Agent] 根据预加载属性生成查询意图: {user_input}")

    # 生成SQL查询
    prompt = SQL_GENERATION_PROMPT.format(user_query=user_input)
    sql_response = llm.invoke(prompt)
    record_llm_usage(sql_response, agent="pokemon_agent")
    
    # 提取SQL语句（移除markdown标记）
    sql = sql_response.content.strip()
    if sql.startswith("```sql") and sql.endswith("```"):
        sql = sql[7:-3].strip()
    elif sql.startswith("```") and sql.endswith("```"):
        sql = sql[3:-3].strip()
    
    sql = sql.replace(";", "").strip()
    print(f"执行的 SQL: {sql}")

    # 执行 SQL
    try:
        from tools.sql_executor import default_executor, format_query_results
        results = default_executor.execute_query(sql)
        result_text = format_query_results(results)
        print(f"查询结果: {results}")
    except Exception as e:
        result_text = f"SQL 执行出错: {str(e)}"
        print(f"SQL 错误: {e}")

    # 更新已执行的代理历史
    executed_agents = state.get("executed_agents_history", [])
    if "pokemon_agent" not in [agent['name'] if isinstance(agent, dict) else agent for agent in executed_agents]:
        executed_agents.append("pokemon_agent")

    # 返回查询结果，并显式传递预加载字段
    return {
        "messages": [AIMessage(content=f"[Pokemon Agent] 查询结果：\n{result_text}")],
        "sql_query": sql,
        "sql_result": result_text,
        "executed_agents_history": executed_agents,
        "step_count": state.get("step_count", 0) + 1,
        "active_skill": state.get("active_skill", ""),
        "compressed_context": state.get("compressed_context", ""),
        # 传递预加载数据
        "preloaded_pokemons": state.get("preloaded_pokemons", []),
        "preloaded_elements": state.get("preloaded_elements", []),
        "preloaded_team": state.get("preloaded_team", []),
    }