from langgraph.graph import StateGraph, START, END
from core.state import multiagentstate
from agents.planner import planner_node
from agents.dispatcher import dispatcher_node, dispatch_route
from agents.rag_agent import rag_agent
from agents.pokemon_agent import pokemon_agent
from agents.summarize import summarize_agent
from agents.team_analyzer import team_analyzer  # 新增

builder = StateGraph(multiagentstate)

# 添加节点
builder.add_node("planner", planner_node)
builder.add_node("dispatcher", dispatcher_node)
builder.add_node("rag_agent", rag_agent)
builder.add_node("pokemon_agent", pokemon_agent)
builder.add_node("summarize", summarize_agent)
builder.add_node("team_analyzer", team_analyzer)          # 新增

# 入口
builder.add_edge(START, "planner")

# planner -> dispatcher
builder.add_edge("planner", "dispatcher")

# 条件路由（在原有基础上添加 team_analyzer）
builder.add_conditional_edges(
    "dispatcher",
    dispatch_route,
    {
        "rag_agent": "rag_agent",
        "pokemon_agent": "pokemon_agent",
        "summarize": "summarize",
        "team_analyzer": "team_analyzer",    # 新增
    }
)

# Agent 完成后返回 dispatcher（team_analyzer 除外）
builder.add_edge("rag_agent", "dispatcher")
builder.add_edge("pokemon_agent", "dispatcher")
# team_analyzer 完成后直接去 summarize（因为它已经完成了所有分析与总结）
builder.add_edge("team_analyzer", "summarize")

# 总结后结束
builder.add_edge("summarize", END)

graph = builder.compile()