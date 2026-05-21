import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from frontend.components.auth import render_login
from frontend.components.sidebar1_pokemon_catalog import render_sidebar
from frontend.components.sidebar3_develop_calculator import render_calculator_sidebar
from frontend.components.sidebar4_damage_calculator import render_damage_calculator_sidebar
from frontend.components.sidebar5_team_builder import render_team_builder_sidebar
from frontend.components.chat import render_chat

st.set_page_config(page_title="OmniPilot", layout="wide")

# ---------- 会话状态初始化 ----------
if "token" not in st.session_state:
    st.session_state.token = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "streaming" not in st.session_state:
    st.session_state.streaming = False
if "selected_pokemon" not in st.session_state:
    st.session_state.selected_pokemon = None
if "pending_pokemon" not in st.session_state:
    st.session_state.pending_pokemon = None
if "pending_attribute_result" not in st.session_state:
    st.session_state.pending_attribute_result = None
if "added_pokemons" not in st.session_state:
    st.session_state.added_pokemons = []
if "added_elements" not in st.session_state:
    st.session_state.added_elements = []
if "show_radar" not in st.session_state:
    st.session_state.show_radar = False
if "show_calculator" not in st.session_state:
    st.session_state.show_calculator = False
if "show_damage_calculator" not in st.session_state:
    st.session_state.show_damage_calculator = False
if "show_team_builder" not in st.session_state:
    st.session_state.show_team_builder = False
if "selected_team" not in st.session_state:
    st.session_state.selected_team = None

# ---------- 登录 ----------
render_login()

st.title("🤖 Roco Kingdom 智能助手")

# ---------- 侧边栏：图鉴 + 计算器入口 ----------
render_sidebar()  # 精灵/属性图鉴

# 根据状态显示对应计算器或入口按钮
if st.session_state.show_calculator:
    render_calculator_sidebar()
elif st.session_state.show_damage_calculator:
    render_damage_calculator_sidebar()
elif st.session_state.show_team_builder:
    render_team_builder_sidebar()
else:
    if not st.session_state.get("streaming", False):
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🧮 培养计算器", use_container_width=True, key="btn_calc"):
                st.session_state.show_calculator = True
                st.rerun()
        with col2:
            if st.button("⚔️ 伤害计算器", use_container_width=True, key="btn_dmg"):
                st.session_state.show_damage_calculator = True
                st.rerun()
        if st.sidebar.button("👥 精灵队伍组建", use_container_width=True, key="btn_team"):
            st.session_state.show_team_builder = True
            st.rerun()

# ---------- 聊天界面 ----------
render_chat()