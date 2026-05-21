import streamlit as st
import httpx
import json

def render_chat():
    # 显示历史消息（只显示用户和助手的对话，不显示系统消息）
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("请输入你的问题..."):
        # 1. 构建本次要发送的消息列表
        messages_to_send = list(st.session_state.messages)  # 复制历史

        # 2. 如果有预加载的精灵，拼成系统消息并附加
        preloaded_pokemons = st.session_state.get("added_pokemons", [])
        if preloaded_pokemons:
            poke_lines = ["【已预加载的精灵信息】"]
            for poke in preloaded_pokemons:
                line = (f"名称: {poke['name']} (No.{poke['national_number']}), "
                        f"属性: {poke['primary_type']}")
                if poke.get('secondary_type'):
                    line += f" + {poke['secondary_type']}"
                line += f", 特性: {poke['ability']}, 种族值总和: {poke['species_total']}"
                if poke.get('stats'):
                    s = poke['stats']
                    line += f", 生命:{s['hp']} 物攻:{s['attack']} 魔攻:{s['sp_attack']} 物防:{s['defense']} 魔防:{s['sp_defense']} 速度:{s['speed']}"
                poke_lines.append(line)
            messages_to_send.append({"role": "system", "content": "\n".join(poke_lines)})

        # 3. 如果有预加载的属性克制信息，同样以系统消息附加
        preloaded_elems = st.session_state.get("added_elements", [])
        if preloaded_elems:
            elem_texts = [item['text'] for item in preloaded_elems]
            elem_content = "【已预加载的属性克制信息】\n" + "\n---\n".join(elem_texts)
            messages_to_send.append({"role": "system", "content": elem_content})
        else:
            elem_texts = []  # 空列表用于 payload

        # 3.5 如果有团队数据，拼成系统消息并附加
        preloaded_team = st.session_state.get("selected_team", [])
        if preloaded_team:
            team_lines = ["【已选择的团队精灵】"]
            for poke in preloaded_team:
                line = (f"名称: {poke['name']} (No.{poke['national_number']}), "
                        f"属性: {poke['primary_type']}")
                if poke.get('secondary_type'):
                    line += f" + {poke['secondary_type']}"
                line += f", 特性: {poke['ability']}, 种族值总和: {poke['species_total']}"
                if poke.get('stats'):
                    s = poke['stats']
                    line += f", HP:{s['hp']} 物攻:{s['attack']} 魔攻:{s['sp_attack']} 物防:{s['defense']} 魔防:{s['sp_defense']} 速度:{s['speed']}"
                # 添加属性克制关系
                if poke.get('attribute_relations'):
                    line += f"\n    属性克制关系:\n    {poke['attribute_relations']}"
                team_lines.append(line)
            team_context = "\n".join(team_lines)
            messages_to_send.append({"role": "system", "content": team_context})

        # 4. 最后把用户当前输入加进去
        messages_to_send.append({"role": "user", "content": user_input})

        # 5. 将用户输入正式添加到会话历史（只保留用户和助手，不包含系统消息）
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 锁定侧边栏
        st.session_state.streaming = True

        url = "http://127.0.0.1:8000/chat/stream"
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        # payload 中传入结构化数据，preloaded_elements 转为纯文本列表
        payload = {
            "messages": messages_to_send,
            "preloaded_pokemons": preloaded_pokemons,
            "preloaded_elements": elem_texts,
            "preloaded_team":st.session_state.get("selected_team", [])   # 新增团队数据
        }

        # frontend/components/chat.py（替换原有的流式循环部分）
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            with st.spinner("正在处理你的问题..."):
                try:
                    with httpx.stream("POST", url, json=payload, headers=headers, timeout=300.0) as response:
                        for line in response.iter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:]
                                try:
                                    event = json.loads(data_str)
                                    etype = event.get("type")
                                    if etype == "token":
                                        full_response += event["content"]
                                        # 纯文本展示，无闪烁光标，避免频繁 Markdown 渲染
                                        response_placeholder.write(full_response)
                                    elif etype == "message":
                                        full_response = event["content"]
                                        # 最终完整消息，用 Markdown 渲染
                                        response_placeholder.markdown(full_response)
                                    elif etype == "error":
                                        full_response = f"❌ 系统错误: {event.get('message', '未知错误')}"
                                        response_placeholder.write(full_response)
                                    elif etype == "done":
                                        # 流结束时，转为最终的 Markdown 渲染
                                        response_placeholder.markdown(full_response)
                                except json.JSONDecodeError:
                                    pass
                except Exception as e:
                    full_response = f"❌ 请求失败: {e}"
                    response_placeholder.write(full_response)
                finally:
                    st.session_state.streaming = False

            if full_response:
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                response_placeholder.warning("⚠️ 未获得有效回答，请重试或检查后端日志")