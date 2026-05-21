import streamlit as st
import httpx
import os
import base64
import time
from frontend.utils import ICON_DIR, get_element_icon_base64, load_element_data

# ---------- 获取属性克制信息 ----------
def get_single_attribute_info(element: str) -> str:
    """获取单属性克制信息"""
    single_data, _ = load_element_data()
    return single_data.get(element, "")

def get_dual_attribute_info(primary: str, secondary: str) -> str:
    """获取双属性克制信息"""
    _, dual_data = load_element_data()
    combo1 = f"{primary}+{secondary}"
    combo2 = f"{secondary}+{primary}"
    return dual_data.get(combo1, dual_data.get(combo2, ""))

def get_pokemon_attribute_relations(pokemon: dict) -> str:
    """获取精灵的属性克制关系文本"""
    primary = pokemon.get('primary_type', '')
    secondary = pokemon.get('secondary_type', '')
    if secondary and secondary != '无':
        return get_dual_attribute_info(primary, secondary)
    return get_single_attribute_info(primary)

# ---------- 后端通信 ----------
BASE = "http://127.0.0.1:8000/api/teams"

def load_team_from_backend(index):
    try:
        resp = httpx.get(f"{BASE}/{index}", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {"name": f"队伍{index}", "pokemons": []}

def save_team_to_backend(index, name, pokemons):
    """保存队伍，包含精灵的属性克制关系"""
    team_data = {
        "name": name,
        "pokemons": []
    }
    for poke in pokemons:
        poke_copy = poke.copy()
        poke_copy["attribute_relations"] = get_pokemon_attribute_relations(poke)
        team_data["pokemons"].append(poke_copy)
    
    try:
        resp = httpx.post(f"{BASE}/{index}", json=team_data, timeout=5)
        return resp.status_code == 200
    except Exception:
        return False

def delete_team_on_backend(index):
    try:
        resp = httpx.delete(f"{BASE}/{index}", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False

# ---------- 精灵列表 ----------
@st.cache_data(ttl=300)
def fetch_pokemon_list():
    try:
        resp = httpx.get("http://127.0.0.1:8000/pokemons", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []

@st.cache_data(ttl=300)
def fetch_pokemon_detail(pid):
    try:
        resp = httpx.get(f"http://127.0.0.1:8000/pokemon/{pid}", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

# ---------- 图片转 base64 ----------
def get_pokemon_icon_base64(national_number):
    path = os.path.join(os.path.dirname(ICON_DIR), "pokemon", f"{national_number}.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{data}"  # 返回完整 data URI
    return ""

# ---------- 主组件 ----------
def render_team_builder_sidebar():
    if st.session_state.get("streaming", False):
        st.info("⏳ 聊天进行中，团队组建暂不可用")
        return

    for i in range(1, 7):
        if f"team_{i}_data" not in st.session_state:
            saved = load_team_from_backend(i)
            st.session_state[f"team_{i}_data"] = {
                "name": saved.get("name", f"队伍{i}"),
                "pokemons": saved.get("pokemons", [])
            }
        if f"team_{i}_clear_confirm" not in st.session_state:
            st.session_state[f"team_{i}_clear_confirm"] = False

    with st.sidebar:
        with st.expander("👥 团队组建", expanded=True):
            if st.button("✖️ 关闭", key="close_team_builder"):
                st.session_state.show_team_builder = False
                st.rerun()

            pokemon_list = fetch_pokemon_list()
            if not pokemon_list:
                st.warning("未获取到精灵列表")
                return

            options = {f"{p['national_number']} - {p['name']}": p for p in pokemon_list}
            option_labels = list(options.keys())

            for i in range(1, 7):
                team = st.session_state[f"team_{i}_data"]
                with st.expander(f"队伍 {i}：{team['name']}", expanded=False):
                    new_name = st.text_input("队伍名称", value=team["name"], key=f"team_name_{i}")
                    if new_name != team["name"]:
                        team["name"] = new_name

                    current = team["pokemons"]
                    st.markdown("**精灵阵容**")
                    cols_per_row = 3
                    for row in range(2):
                        cols = st.columns(cols_per_row)
                        for col_idx in range(cols_per_row):
                            slot_index = row * cols_per_row + col_idx
                            if slot_index < len(current):
                                poke = current[slot_index]
                                with cols[col_idx]:
                                    _render_pokemon_card(poke, i, slot_index)
                            else:
                                with cols[col_idx]:
                                    if slot_index == len(current) and len(current) < 6:
                                        st.markdown("<div style='height:100px; border:1px dashed #aaa; border-radius:8px; display:flex; align-items:center; justify-content:center;'>空位</div>", unsafe_allow_html=True)
                                    else:
                                        st.markdown("<div style='height:100px; border:1px dashed #aaa; border-radius:8px;'></div>", unsafe_allow_html=True)

                    if len(current) < 6:
                        st.markdown("---")
                        col_sel, col_btn = st.columns([3, 1])
                        with col_sel:
                            selected_label = st.selectbox(
                                "选择精灵",
                                option_labels,
                                key=f"add_select_{i}"
                            )
                        with col_btn:
                            if st.button("✅ 添加", key=f"add_confirm_{i}"):
                                if selected_label:
                                    poke_data = options[selected_label]
                                    existing_ids = [p['id'] for p in current]
                                    if poke_data['id'] in existing_ids:
                                        st.error("该精灵已在队伍中，不能重复添加。")
                                    else:
                                        detail = fetch_pokemon_detail(poke_data["id"])
                                        if detail:
                                            team["pokemons"].append(detail)
                                            st.rerun()
                                        else:
                                            st.error("获取精灵详情失败")
                    else:
                        st.info("队伍已满（最多6只）")

                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("💾 保存", key=f"save_{i}"):
                            if save_team_to_backend(i, team["name"], team["pokemons"]):
                                st.success(f"队伍{i}已保存")
                            else:
                                st.error("保存失败")
                    with col2:
                        if st.button("🗑️ 清空", key=f"clear_{i}"):
                            st.session_state[f"team_{i}_clear_confirm"] = True
                    with col3:
                        if st.button("🔍 分析", key=f"analyze_{i}"):
                            if not team["pokemons"]:
                                st.warning("请先添加精灵")
                            else:
                                # 构建包含属性克制关系的队伍数据
                                team_with_relations = []
                                for poke in team["pokemons"]:
                                    poke_copy = poke.copy()
                                    poke_copy["attribute_relations"] = get_pokemon_attribute_relations(poke)
                                    team_with_relations.append(poke_copy)
                                st.session_state.selected_team = team_with_relations
                                st.session_state.team_name = team["name"]
                                time.sleep(0.5)
                                st.rerun()

                    if st.session_state[f"team_{i}_clear_confirm"]:
                        st.warning("保存的全部内容都会删除，确定要清空吗？")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("是", key=f"clear_yes_{i}"):
                                team["name"] = f"队伍{i}"
                                team["pokemons"] = []
                                st.session_state[f"team_{i}_clear_confirm"] = False
                                delete_team_on_backend(i)
                                st.rerun()
                        with c2:
                            if st.button("否", key=f"clear_no_{i}"):
                                st.session_state[f"team_{i}_clear_confirm"] = False
                                st.rerun()

def _render_pokemon_card(poke, team_idx, slot_idx):
    nat = poke.get('national_number', '')
    img_src = get_pokemon_icon_base64(nat)
    primary = poke.get('primary_type', '')
    secondary = poke.get('secondary_type', '')

    primary_b64 = get_element_icon_base64(primary) if primary else ""
    secondary_b64 = get_element_icon_base64(secondary) if secondary else ""

    html = f"""
    <div style='border:1px solid #ccc; border-radius:8px; padding:4px; text-align:center; margin-bottom:4px;'>
        <div style='display:flex; justify-content:center; align-items:center; height:70px;'>
    """
    if img_src:
        html += f"<img src='{img_src}' style='max-width:100px; max-height:100px;'/>"
    else:
        html += "<span style='font-size:24px;'>❓</span>"
    html += "</div>"
    html += f"<div style='font-weight:bold; font-size:12px; margin-top:2px;'>{poke['name']}</div>"
    html += "<div style='display:flex; justify-content:center; align-items:center; gap:2px; margin-top:2px;'>"
    if primary_b64:
        html += f"<img src='{primary_b64}' style='width:45px; height:45px;' title='{primary}'>"
    else:
        html += primary
    if secondary_b64:
        html += f"<img src='{secondary_b64}' style='width:45px; height:45px;' title='{secondary}'>"
    elif secondary:
        html += secondary
    html += "</div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    if st.button("🗑️ 删除", key=f"del_card_{team_idx}_{slot_idx}"):
        team = st.session_state[f"team_{team_idx}_data"]
        team["pokemons"].pop(slot_idx)
        st.rerun()