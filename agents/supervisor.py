
from langchain_core.messages import HumanMessage, AIMessage
from core.metrics import record_llm_usage   # 新增导入

from core.state import multiagentstate
from core.llm import llm

# 导入新 Agent
from agents.rag_agent import rag_agent
from agents.pokemon_agent import data_analyst_agent


# ========== 专家 Agent（通用型） ==========

def researcher_agent(state: multiagentstate):
    """通用研究员，回答不受限于知识库的问题"""
    print("[研究员] 正在研究...")
    # 获取用户查询 - 优先使用原始查询，否则使用最新消息
    user_query = state.get("original_query", "")
    if not user_query and state.get("messages"):
        last_message = state["messages"][-1]
        user_query = last_message.content if hasattr(last_message, 'content') else str(last_message)
    if not user_query:
        user_query = "请提供帮助"
    
    research_result = llm.invoke(
        f"你现在是一位高级研究员，请研究用户的问题：{user_query}，并给出研究结果"
    )
    record_llm_usage(research_result, agent="researcher")   # ✅ 新增
    return {
        "messages": [AIMessage(content=research_result.content)],
    }
 


# ========== Supervisor ==========