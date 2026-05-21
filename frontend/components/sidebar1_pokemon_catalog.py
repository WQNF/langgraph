import streamlit as st
import os
import httpx
from frontend.utils import (
    ICON_DIR, get_element_icon_base64,
    parse_single_relations, parse_dual_relations,
    load_element_data
)
import time
from frontend.components.sidebar2_attribute_catalog import render_element_pokedex


def show_added_items():
    with st.sidebar:
        st.markdown(
            "<h2 style='text-align: center; margin-bottom: 10px;'>📦 预加载信息</h2>",
            unsafe_allow_html=True
        )

        has_pokemons = st.session_state.get("added_pokemons")
        has_elements = st.session_state.get("added_elements")
        selected_team = st.session_state.get("selected_team")

        if not has_pokemons and not has_elements and not selected_team:
            st.markdown(
                "<p style='text-align: center; color: gray;'>暂无预加载内容</p>",
                unsafe_allow_html=True
            )
            return

        # 精灵
        if has_pokemons:
            with st.expander("🟢 精灵", expanded=False):
                for poke in list(has_pokemons):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        sec = f"/{poke['secondary_type']}" if poke.get('secondary_type') else ""
                        st.markdown(f"{poke['name']} ({poke['primary_type']}{sec})")
                    with col2:
                        if st.button("❌", key=f"del_poke_{poke['id']}"):
                            st.session_state.added_pokemons = [
                                p for p in st.session_state.added_pokemons if p['id'] != poke['id']
                            ]
                            st.rerun()

        # 属性
        if has_elements:
            with st.expander("🔵 属性信息", expanded=False):
                for i, item in enumerate(list(has_elements)):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        primary = item['primary']
                        secondary = item['secondary']
                        is_dual = item['is_dual']
                        p_b64 = get_element_icon_base64(primary)
                        icon_part = f'<img src="{p_b64}" width="40" height="40" style="vertical-align: middle; margin-right: 2px;">'
                        if is_dual and secondary != "无":
                            s_b64 = get_element_icon_base64(secondary)
                            if s_b64:
                                icon_part += f'<img src="{s_b64}" width="40" height="40" style="vertical-align: middle; margin-right: 2px;">'
                        attr_name = primary if not is_dual else f"{primary} + {secondary}"
                        st.markdown(
                            f"**{i+1}.** {icon_part} {attr_name}",
                            unsafe_allow_html=True
                        )
                    with col2:
                        if st.button("❌", key=f"del_elem_{item['id']}"):
                            st.session_state.added_elements = [
                                e for e in st.session_state.added_elements if e['id'] != item['id']
                            ]
                            st.rerun()

        # 队伍
        if selected_team:
            with st.expander("🟠 队伍", expanded=False):
                team_name = st.session_state.get("team_name", "自定义队伍")
                poke_count = len(selected_team)
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"{team_name} ({poke_count} 只)")
                with col2:
                    if st.button("❌", key="del_team"):
                        st.session_state.selected_team = None
                        st.rerun()
                for poke in selected_team:
                    sec = f"/{poke['secondary_type']}" if poke.get('secondary_type') else ""
                    st.markdown(f"- {poke['name']} ({poke['primary_type']}{sec})")

def render_sidebar():
    if st.session_state.get("streaming", False):
        with st.sidebar:
            st.info("⏳ 聊天进行中，图鉴暂不可用")
        st.stop()

    if "selected_pokemon" not in st.session_state:
        st.session_state.selected_pokemon = None
    if "pending_pokemon" not in st.session_state:
        st.session_state.pending_pokemon = None
    if "pending_attribute_result" not in st.session_state:
        st.session_state.pending_attribute_result = None

    with st.sidebar:
        show_added_items()
        st.divider()
        st.markdown(
            "<h2 style='text-align: center; margin-top: 10px;'>🛠️ 实用工具</h2>",
            unsafe_allow_html=True
        )
        with st.expander("🧬 精灵图鉴", expanded=False):
            st.markdown(
                "<h2 style='text-align: center;'>🧬 精灵图鉴</h2>",
                unsafe_allow_html=True
            )

            @st.cache_data(ttl=300)
            def fetch_pokemon_list():
                try:
                    resp = httpx.get("http://127.0.0.1:8000/pokemons", timeout=10)
                    if resp.status_code == 200:
                        return resp.json()
                except Exception:
                    pass
                return []

            pokemon_list = fetch_pokemon_list()
            if pokemon_list:
                options = {f"{p['national_number']} - {p['name']}": p for p in pokemon_list}
                options_list = list(options.keys())

                selected_label = st.selectbox("选择精灵", list(options.keys()), key="pokemon_select")

                if selected_label:
                    selected_data = options[selected_label]
                    pokemon_id = selected_data["id"]
                    national_number = selected_data.get("national_number", "")

                    @st.cache_data(ttl=300)
                    def fetch_pokemon_detail(pid):
                        try:
                            resp = httpx.get(f"http://127.0.0.1:8000/pokemon/{pid}", timeout=10)
                            if resp.status_code == 200:
                                return resp.json()
                        except Exception:
                            pass
                        return None

                    detail = fetch_pokemon_detail(pokemon_id)
                    if detail:
                        st.session_state.selected_pokemon = detail

                        col_img, col_info = st.columns([1, 3])
                        with col_img:
                            icon_path = os.path.join(os.path.dirname(ICON_DIR), "pokemon", f"{national_number}.png")
                            if os.path.exists(icon_path):
                                st.image(icon_path, width=128)
                            else:
                                st.markdown("❓")

                        with col_info:
                            st.markdown(f"**{detail['name']}** (No. {national_number})")
                            primary_b64 = get_element_icon_base64(detail['primary_type'])
                            if detail.get('secondary_type'):
                                secondary_b64 = get_element_icon_base64(detail['secondary_type'])
                                icon_html = (
                                    f'<img src="{primary_b64}" width="70" height="70" style="margin-right:0px;">'
                                    f'<img src="{secondary_b64}" width="70" height="70" style="margin-left:0px;">'
                                )
                                st.markdown(icon_html, unsafe_allow_html=True)
                            else:
                                if primary_b64:
                                    st.image(primary_b64, width=60)

                        with st.expander("详细数据"):
                            st.markdown(f"**种族值总和:** {detail.get('species_total', 0)}")
                            if detail.get("stats"):
                                stats = detail["stats"]
                                st.markdown(f"**特性:**  {detail.get('ability', '无')}")
                                st.markdown(
                                    f"**生命:** {stats['hp']}   | **物攻:** {stats['attack']}   | **魔攻:** {stats['sp_attack']}  \n"
                                    f"**物防:** {stats['defense']}   | **魔防:** {stats['sp_defense']}   | **速度:** {stats['speed']}"
                                )

                        if st.button("📤 将当前精灵加入预加载"):
                            if not any(p['id'] == detail['id'] for p in st.session_state.added_pokemons):
                                if len(st.session_state.added_pokemons) >= 6:
                                    st.warning("⚠️ 最多添加 6 只精灵，请先删除部分")
                                else:
                                    st.session_state.added_pokemons.append(detail)
                                    st.success(f"✅ 已添加 {detail['name']}")
                                    time.sleep(0.5)
                                    st.rerun()
                            else:
                                st.info(f"{detail['name']} 已在预加载列表中")
                    else:
                        st.warning("无法获取精灵详细信息")
        # 属性图鉴
        render_element_pokedex()