# test_planner.py
"""
Planner 调试脚本：模拟预加载迪莫信息，测试 Planner 是否能正确路由
"""
import sys
import os

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from agents.planner import planner_node

# ----- 构造模拟状态 -----
# 迪莫的完整信息（与前端传递给后端的数据格式一致）
dimo_pokemon = {
    "id": 1,
    "national_number": "001",
    "name": "迪莫",
    "primary_type": "光系",
    "secondary_type": None,
    "species_total": 582,
    "ability": "最好的伙伴：造成克制伤害后，获得攻防速+20%，并回复2能量。",
    "stats": {
        "hp": 120,
        "attack": 80,
        "defense": 105,
        "sp_attack": 80,
        "sp_defense": 105,
        "speed": 92
    }
}

# 模拟消息历史：通常包含系统消息（预加载数据）和用户问题
# 我们直接以用户问题作为 HumanMessage，不添加系统消息，因为预加载数据主要通过 state["preloaded_pokemons"] 传递
messages = [
    HumanMessage(content="给出这只精灵的信息"),        # 第一轮提问（可选）
    AIMessage(content="名称: 迪莫 ... 属性: 光系 ..."), # 助手之前的回答（这里模拟有属性信息的上下文）
]

# 状态字典（只需要 Planner 用到的字段）
state = {
    "messages": messages,                     # 对话历史
    "user_input": "他的属性克制哪些？",        # 当前问题
    "preloaded_pokemons": [dimo_pokemon],     # 预加载精灵列表
    "preloaded_elements": [],                 # 预加载属性信息
    "need_agents": [],                        # Planner 会自动填充
    "active_skill": "",
    "compressed_context": "",                 # 记忆压缩摘要（暂无）
    "plan": [],
    "step_count": 0,
}

print("=== 测试 Planner（预加载迪莫，问“他的属性克制哪些？”） ===\n")
print("[状态摘要]")
print(f"预加载精灵数量: {len(state['preloaded_pokemons'])}")
if state['preloaded_pokemons']:
    poke = state['preloaded_pokemons'][0]
    print(f"精灵姓名: {poke['name']} ({poke['primary_type']})")
print(f"当前用户输入: {state['user_input']}")
print("--" * 30)

# 调用 Planner
result = planner_node(state)

# 输出 Planner 的决策
print("\n[Planner 输出]")
print(f"need_agents: {result.get('need_agents')}")
print(f"active_skill: {result.get('active_skill')}")
print(f"relation: {result.get('relation')}")
print(f"plan: {result.get('plan')}")

# 检查是否符合预期
need = result.get("need_agents", [])
if need == ["rag_agent"]:
    print("\n✅ 正确：Planner 识别到需要 RAG Agent 去查光系的克制关系")
elif need == []:
    print("\n⚠️  Planner 认为不需要任何 Agent（可能直接总结），请检查总结结果是否正确")
elif "pokemon_agent" in need:
    print("\n❌ 错误：Planner 仍然要调用 pokemon_agent，说明预加载数据未被识别")
else:
    print(f"\n🤔 意外返回: {need}")