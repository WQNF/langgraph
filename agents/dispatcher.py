# agents/dispatcher.py
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Send

def dispatcher_node(state: dict):
    """根据需要执行的专家列表和已有信息来决定下一步"""
    print("=================")
    print("【已进入节点-dispatcher】")

    # 使用现有的消息历史
    messages = state.get("messages", [])
    user_input = state.get("user_input", "")
    if len(messages) == 0 and user_input:
        messages = [HumanMessage(content=user_input)]

    # 获取需要执行的专家列表和已执行的历史
    need_agents = state.get("need_agents", [])
    executed_history = state.get("executed_agents_history", [])
    relation = state.get("relation", "serial")

    # 提取已执行的专家名称
    executed_agent_names = [item['name'] if isinstance(item, dict) else item for item in executed_history]
    pending_agents = [agent for agent in need_agents if agent not in executed_agent_names]

    print(f"[Dispatcher]需要执行的专家: {need_agents}")
    print(f"[Dispatcher]已执行的专家: {executed_agent_names}")
    print(f"[Dispatcher]待执行的专家: {pending_agents}")
    print(f"[Dispatcher]执行模式: {relation}")

    # 公共字段：确保预加载数据在每次返回时都传递
    common_fields = {
        "preloaded_pokemons": state.get("preloaded_pokemons", []),
        "preloaded_elements": state.get("preloaded_elements", []),
        "preloaded_team": state.get("preloaded_team", []),   # 预留
        "active_skill": state.get("active_skill", ""),
        "compressed_context": state.get("compressed_context", ""),
    }

    if pending_agents:
        if relation == "parallel" and len(pending_agents) > 1:
            # 并行模式：一次性分发所有待执行专家
            return {
                "next_agent": "__parallel__",
                "executed_agents_history": executed_history,
                "step_count": state.get("step_count", 0) + 1,
                "relation": relation,
                "need_agents": need_agents,
                **common_fields
            }
        else:
            # 串行模式：逐个执行
            next_agent = pending_agents[0]
            updated_executed_history = executed_history.copy()
            updated_executed_history.append(next_agent)
            print(f"[Dispatcher]分发任务给专家: {next_agent}")
            return {
                "next_agent": next_agent,
                "executed_agents_history": updated_executed_history,
                "step_count": state.get("step_count", 0) + 1,
                "relation": relation,
                "need_agents": need_agents,
                **common_fields
            }
    else:
        # 没有待执行专家，转向总结节点
        print("[Dispatcher] 所有任务已完成，转向总结节点")
        return {
            "next_agent": "summarize",
            "task_completed": True,
            "messages": [],
            "step_count": state.get("step_count", 0) + 1,
            "relation": relation,
            "need_agents": need_agents,
            **common_fields
        }


def dispatch_route(state: dict):
    """路由函数，根据当前状态决定下一步，支持并行扇出"""
    next_agent = state.get("next_agent", "rag_agent")
    if next_agent == "team_analyzer":
        return [Send("team_analyzer", state)]

    # 并行扇出：一次性返回所有待执行专家的 Send
    if next_agent == "__parallel__":
        need_agents = state.get("need_agents", [])
        executed_history = state.get("executed_agents_history", [])
        executed_agent_names = [item['name'] if isinstance(item, dict) else item for item in executed_history]
        pending_agents = [a for a in need_agents if a not in executed_agent_names]

        if pending_agents:
            print(f"[Dispatcher] 并行分发: {pending_agents}")
            return [Send(agent, state) for agent in pending_agents]
        else:
            # 没有待执行专家，直接转向summarize
            return [Send("summarize", state)]

    # 串行路由
    if next_agent == "summarize":
        return [Send("summarize", state)]
    elif next_agent == "rag_agent":
        return [Send("rag_agent", state)]
    elif next_agent == "pokemon_agent":
        return [Send("pokemon_agent", state)]
    else:
        # 默认回退
        return [Send("rag_agent", state)]