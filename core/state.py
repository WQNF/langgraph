from typing import TypedDict, Annotated, List, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
import operator
from operator import add
from typing import Optional

class multiagentstate(TypedDict):
    # 用户输入
    user_input: str
    # 消息记录
    messages: Annotated[list[BaseMessage], add]
    #rag_agent输出
    rag_agent_output: str
    #pokemon_agent输出
    pokemon_agent_output: str
    # 可用专家
    available_experts: list[str]
    # 需要调用的专家
    need_agents: list[str]
    # 已调用的专家
    executed_agents_history: Annotated[list[str], operator.add]
    # 当前激活的技能
    active_skill: Annotated[str, lambda x, y: y if y else x]
    # 压缩后的历史摘要文本
    compressed_context: Annotated[str, lambda x, y: y if y else x]
    recent_messages: Annotated[list[BaseMessage], add]  
    # 关系
    relation: str
    preloaded_pokemons: list       # 预加载的精灵列表
    preloaded_elements: list       # 预加载的属性信息列表
    preloaded_team : list          # 预加载的队伍列表


   