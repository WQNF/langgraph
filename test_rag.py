# test_rag.py
"""
RAG Agent 调试脚本：模拟预加载迪莫信息，测试 RAG 是否能提取出光系属性
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_core.messages import HumanMessage, AIMessage
from agents.rag_agent import rag_agent  # 注意文件名可能是 rag_agent.py 或 rag.py，根据实际调整

# 模拟迪莫预加载数据（与前序测试一致）
dimo_pokemon = {
    "id": 1,
    "national_number": "001",
    "name": "迪莫",
    "primary_type": "光系",
    "secondary_type": None,
    "species_total": 582,
    "ability": "最好的伙伴：造成克制伤害后，获得攻防速+20%，并回复2能量。",
    "stats": {
        "hp": 120, "attack": 80, "defense": 105,
        "sp_attack": 80, "sp_defense": 105, "speed": 92
    }
}

# 模拟对话历史：与 Planner 测试类似
messages = [
    HumanMessage(content="给出这只精灵的信息"),
    AIMessage(content="名称: 迪莫 ... 属性: 光系 ..."),   # 这里包含“属性: 光系”是关键
]

state = {
    "messages": messages,
    "user_input": "他的属性克制哪些？",
    "preloaded_pokemons": [dimo_pokemon],     # 预加载精灵列表
    "preloaded_elements": [],
    "need_agents": [],
    "active_skill": "type_analysis",
    "executed_agents_history": [],
    "step_count": 0,
    "compressed_context": "",
}

print("=== 测试 RAG Agent（预加载迪莫，问“他的属性克制哪些？”） ===\n")
print("[状态摘要]")
print(f"预加载精灵: {dimo_pokemon['name']} ({dimo_pokemon['primary_type']})")
print(f"历史消息最后一条: {messages[-1].content[:50]}...")
print(f"当前用户输入: {state['user_input']}")
print("--" * 30)

# 调用 RAG Agent
result = rag_agent(state)

# 输出关键信息
print("\n[RAG Agent 返回的消息内容（前 300 字符）]")
print("=============================================")
if result.get("messages"):
    print(result)
    #print(result["messages"][-1].content[:300])
print("=============================================")
print("\n[检索到的文档数量]", len(result.get("context_docs", [])))
if result["context_docs"]:
    print("第一篇文档开头:", result["context_docs"][0][:100])
else:
    print("⚠️ 未检索到任何文档！")

# 检查是否命中光系
found_light = False
for doc in result.get("context_docs", []):
    if "【光系】" in doc or "光系" in doc:
        found_light = True
        break
if found_light:
    print("\n✅ 成功检索到光系克制文档")
else:
    print("\n❌ 未能检索到光系文档，属性提取失败")