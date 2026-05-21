import streamlit as st
import httpx

def render_login() -> bool:
    """渲染登录界面，登录成功返回 True，否则 st.stop()"""
    if st.session_state.token is not None:
        return True

    st.title("🔐 登录 Roco Kingdom")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    if st.button("登录"):
        try:
            resp = httpx.post(
                "http://127.0.0.1:8000/token",
                data={"username": username, "password": password}
            )
            if resp.status_code == 200:
                st.session_state.token = resp.json()["access_token"]
                st.rerun()
            else:
                st.error("用户名或密码错误")
        except Exception as e:
            st.error(f"无法连接后端: {e}")
    st.stop()