import json
import os
from typing import List, Dict, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from prometheus_fastapi_instrumentator import Instrumentator
from core.graph import graph
from api.dependencies.auth import (
    authenticate_user,
    create_access_token,
    Token,
    fake_users_db,
    get_current_user,
    User
)

app = FastAPI(title="OmniPilot API")
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)


# ==================== 队伍数据存储目录 ====================
TEAM_DIR = r"D:\Python_exercise\rock_kingdom\data\teams"
os.makedirs(TEAM_DIR, exist_ok=True)

def _team_path(team_index: int) -> str:
    return os.path.join(TEAM_DIR, f"team_{team_index}.json")


# ==================== 精灵查询接口 ====================
@app.get("/pokemons")
async def list_pokemons():
    """返回所有精灵的简要列表，用于下拉选择"""
    from tools.sql_executor import default_executor
    results = default_executor.execute_query(
        "SELECT id, national_number, name, primary_type, secondary_type FROM pokemon ORDER BY national_number"
    )
    return results


@app.get("/pokemon/{pokemon_id}")
async def get_pokemon_detail(pokemon_id: int):
    """返回精灵完整信息，包括种族值、属性、特性等"""
    from tools.sql_executor import default_executor
    pokemon = default_executor.execute_query(
        "SELECT * FROM pokemon WHERE id = %s", (pokemon_id,)
    )
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    stats = default_executor.execute_query(
        "SELECT * FROM pokemon_stats WHERE pokemon_id = %s", (pokemon_id,)
    )
    detail = pokemon[0]
    detail["stats"] = stats[0] if stats else None
    return detail


# ==================== 队伍保存/加载/删除接口 ====================
@app.get("/api/teams/{team_index}")
async def load_team(team_index: int):
    """加载指定队伍"""
    path = _team_path(team_index)
    if not os.path.exists(path):
        return {"name": f"队伍{team_index}", "pokemons": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/teams/{team_index}")
async def save_team(team_index: int, team: dict):
    """保存指定队伍"""
    path = _team_path(team_index)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(team, f, ensure_ascii=False, indent=2)
    return {"status": "ok"}


@app.delete("/api/teams/{team_index}")
async def delete_team(team_index: int):
    """删除指定队伍"""
    path = _team_path(team_index)
    if os.path.exists(path):
        os.remove(path)
    return {"status": "deleted"}


# ==================== 聊天模型 ====================
class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    preloaded_pokemons: Optional[List[Dict]] = None
    preloaded_elements: Optional[List[str]] = None
    preloaded_team: Optional[List[Dict]] = None   # 新增团队字段


class ChatResponse(BaseModel):
    reply: str


def get_last_user_input(messages: List[Dict[str, str]]) -> str:
    """从消息列表中提取最后一条用户消息的内容"""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return msg["content"]
    return ""


# ==================== 非流式端点 ====================
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    initial_state = {
        "messages": [HumanMessage(content=m["content"]) for m in req.messages if m["role"] == "user"],
        "user_input": get_last_user_input(req.messages),
        "available_experts": ["rag_agent", "pokemon_agent"],
        "need_agents": [],
        "executed_agents_history": [],
        "next_agent": "planner",
        "task_completed": False,
        "visited_agents": [],
        "step_count": 0,
        "plan": [],
        "user_id": "default_user",
        "department": "general",
    }
    result = graph.invoke(initial_state)
    reply = result["messages"][-1].content if result.get("messages") else ""
    return ChatResponse(reply=reply)


# ==================== 登录端点 ====================
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticator": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username, "department": user.department}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ==================== 流式端点 ====================
# api/main.py（只替换 chat_stream 函数体）

# api/main.py 中的 chat_stream 函数

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest, current_user: User = Depends(get_current_user)):
    async def event_generator():
        # 构建 input_state（与之前相同，确保包含 preloaded_team）
        input_messages = []
        for m in req.messages:
            if m["role"] == "user":
                input_messages.append(HumanMessage(content=m["content"]))
            elif m["role"] == "assistant":
                input_messages.append(AIMessage(content=m["content"]))

        input_state = {
            "messages": input_messages,
            "user_input": get_last_user_input(req.messages),
            "available_experts": ["rag_agent", "pokemon_agent"],
            "need_agents": [],
            "executed_agents_history": [],
            "next_agent": "planner",
            "task_completed": False,
            "visited_agents": [],
            "step_count": 0,
            "plan": [],
            "user_id": current_user.username,
            "department": current_user.department,
            "preloaded_pokemons": req.preloaded_pokemons or [],
            "preloaded_elements": req.preloaded_elements or [],
            "preloaded_team": req.preloaded_team or [],   # 务必加上
        }

        try:
            # 使用异步 stream_mode="custom" 来接收 writer 发送的自定义事件
            for chunk in graph.stream(input_state, stream_mode="custom"):
                # chunk 就是 writer({"token": ...}) 发送的内容
                if isinstance(chunk, dict) and "token" in chunk:
                    token = chunk["token"]
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")