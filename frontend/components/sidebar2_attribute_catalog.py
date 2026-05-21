import streamlit as st
import os
import time
import uuid
from frontend.utils import (
    ICON_DIR, get_element_icon_base64,
    parse_single_relations, parse_dual_relations,
    load_element_data
)


def render_element_pokedex():
    if st.session_state.get("streaming", False):
        st.info("⏳ 聊天进行中，图鉴暂不可用")
        return

    if "last_element_result" not in st.session_state:
        st.session_state.last_element_result = ""

    single_data, dual_data = load_element_data()

    # 整个图鉴包裹在可折叠的 expander 中
    with st.expander("📖 属性图鉴", expanded=False):
        # 移除原来的 st.container(border=True)
        st.markdown(
            "<h2 style='text-align: center;'>📖 属性图鉴</h2>",
            unsafe_allow_html=True
        )

        all_elements = [
            "火系", "水系", "草系", "光系", "恶系", "幽系",
            "普通系", "地系", "冰系", "龙系", "电系", "毒系",
            "虫系", "武系", "翼系", "萌系", "机械系", "幻系"
        ]

        # 主属性
        col1, col2 = st.columns([3, 1])
        with col1:
            primary = st.selectbox("主属性", all_elements, index=0, key="primary")
        with col2:
            icon_path = os.path.join(ICON_DIR, f"{primary}.png")
            if os.path.exists(icon_path):
                st.image(icon_path, width=60)
                st.caption(primary)
            else:
                st.write(primary)

        # 副属性
        col3, col4 = st.columns([3, 1])
        with col3:
            secondary = st.selectbox("副属性", ["无"] + all_elements, index=0, key="secondary")
        with col4:
            if secondary != "无":
                icon_path2 = os.path.join(ICON_DIR, f"{secondary}.png")
                if os.path.exists(icon_path2):
                    st.image(icon_path2, width=60)
                    st.caption(secondary)
                else:
                    st.write(secondary)
            else:
                st.write("无")

        is_dual = (secondary != "无" and secondary != primary)

        # ---------- 按钮行（始终并排）----------
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            search_clicked = st.button(
                "🔎 查询克制关系",
                disabled=st.session_state.get("streaming", False)
            )
        with col_btn2:
            # 始终渲染按钮，无结果时禁用
            has_result = bool(st.session_state.get("last_element_result"))
            add_clicked = st.button(
                "📤 把结果加入聊天",
                key="add_result_to_chat",
                disabled=not has_result
            )
            if add_clicked and has_result:
                # 去重检查（基于属性组合）
                def already_exists(primary, secondary, is_dual):
                    for item in st.session_state.added_elements:
                        if item['is_dual'] == is_dual:
                            if is_dual:
                                existing = {item['primary'], item['secondary']}
                                current = {primary, secondary}
                                if existing == current:
                                    return True
                            else:
                                if item['primary'] == primary:
                                    return True
                    return False

                if already_exists(primary, secondary, is_dual):
                    st.info("该属性信息已在预加载列表中，无需重复添加。")
                else:
                    if len(st.session_state.added_elements) >= 6:
                        st.warning("⚠️ 最多添加6组属性信息，请先删除部分。")
                    else:
                        text = f"📌 属性查询结果：\n\n{st.session_state.last_element_result}"
                        new_item = {
                            "id": str(uuid.uuid4()),
                            "text": text,
                            "primary": primary,
                            "secondary": secondary,
                            "is_dual": is_dual
                        }
                        st.session_state.added_elements.append(new_item)
                        st.success("✅ 已添加属性克制信息到预加载列表")
                        time.sleep(0.5)
                        st.rerun()

        # ---------- 查询逻辑 ----------
        if search_clicked:
            if secondary == primary and primary != "无":
                st.warning("主属性和副属性不能相同")
            else:
                result_text = ""
                relations = None

                if not is_dual:
                    if primary in single_data:
                        raw = single_data[primary]
                        relations = parse_single_relations(raw)
                        result_text = raw
                    else:
                        st.info(f"未找到 {primary} 的克制数据")
                else:
                    e1, e2 = primary, secondary
                    combo1 = f"{e1}+{e2}"
                    combo2 = f"{e2}+{e1}"
                    if combo1 in dual_data:
                        raw = dual_data[combo1]
                        relations = parse_dual_relations(raw)
                        result_text = raw
                    elif combo2 in dual_data:
                        raw = dual_data[combo2]
                        relations = parse_dual_relations(raw)
                        result_text = raw
                    else:
                        parts = []
                        if e1 in single_data:
                            parts.append(single_data[e1])
                        if e2 in single_data:
                            parts.append(single_data[e2])
                        if parts:
                            result_text = "\n\n".join(parts)
                        else:
                            st.info("未找到对应的克制数据")
                        relations = None

                # 展示结果
                if relations:
                    st.markdown("### 属性查询结果")
                    if not is_dual:
                        # 单属性展示
                        for title in ["我克制", "我抵抗", "抵抗我", "克制我"]:
                            items = relations.get(title, [])
                            st.markdown(f"**{title}**")
                            if not items:
                                st.write("无")
                            else:
                                html_icons = ""
                                for elem in items:
                                    b64 = get_element_icon_base64(elem)
                                    if b64:
                                        html_icons += (
                                            f'<span style="display:inline-block; text-align:center; margin:5px; vertical-align:top;">'
                                            f'<img src="{b64}" width="56" height="56" title="{elem}"><br>'
                                            f'<span style="font-size:12px;">{elem}</span></span>'
                                        )
                                    else:
                                        html_icons += f'<span style="margin:5px; font-size:14px;">{elem}</span>'
                                st.markdown(html_icons, unsafe_allow_html=True)
                    else:
                        # ----- 双属性展示（完整恢复） -----
                        st.markdown("**我克制**")
                        for skill_title, targets in relations["我克制"]:
                            st.markdown(f"*{skill_title}*")
                            if targets:
                                html = ""
                                for t in targets:
                                    b64 = get_element_icon_base64(t)
                                    if b64:
                                        html += (
                                            f'<span style="display:inline-block; text-align:center; margin:5px; vertical-align:top;">'
                                            f'<img src="{b64}" width="56" height="56" title="{t}"><br>'
                                            f'<span style="font-size:12px;">{t}</span></span>'
                                        )
                                    else:
                                        html += f'<span style="margin:5px; font-size:14px;">{t}</span>'
                                st.markdown(html, unsafe_allow_html=True)
                            else:
                                st.write("无")

                        st.markdown("**我抵抗**")
                        resist_items = relations["我抵抗"]
                        if resist_items:
                            strong = [(e, t) for (e, t) in resist_items if "强力" in t]
                            normal = [(e, t) for (e, t) in resist_items if "强力" not in t]
                            html_resist = ""
                            for elem, tag in strong + normal:
                                b64 = get_element_icon_base64(elem)
                                if b64:
                                    if tag:
                                        html_resist += (
                                            f'<span style="display:inline-block; text-align:center; margin:5px; vertical-align:top;">'
                                            f'<img src="{b64}" width="56" height="56" title="{elem}"><br>'
                                            f'<span style="font-size:12px;">{elem}</span><br>'
                                            f'<span style="font-size:10px; font-weight:bold;">{tag}</span>'
                                            f'</span>'
                                        )
                                    else:
                                        html_resist += (
                                            f'<span style="display:inline-block; text-align:center; margin:5px; vertical-align:top;">'
                                            f'<img src="{b64}" width="56" height="56" title="{elem}"><br>'
                                            f'<span style="font-size:12px;">{elem}</span>'
                                            f'</span>'
                                        )
                                else:
                                    html_resist += f'<span style="margin:5px; font-size:14px; font-weight:bold;">{elem} {tag}</span>' if tag else f'<span style="margin:5px; font-size:14px;">{elem}</span>'
                            st.markdown(html_resist, unsafe_allow_html=True)
                        else:
                            st.write("无")

                        st.markdown("**克制我**")
                        weak_items = relations["克制我"]
                        if weak_items:
                            strong = [(e, t) for (e, t) in weak_items if "强力" in t]
                            normal = [(e, t) for (e, t) in weak_items if "强力" not in t]
                            html_weak = ""
                            for elem, tag in strong + normal:
                                b64 = get_element_icon_base64(elem)
                                if b64:
                                    if tag:
                                        html_weak += (
                                            f'<span style="display:inline-block; text-align:center; margin:5px; vertical-align:top;">'
                                            f'<img src="{b64}" width="56" height="56" title="{elem}"><br>'
                                            f'<span style="font-size:12px;">{elem}</span><br>'
                                            f'<span style="font-size:10px; font-weight:bold;">{tag}</span>'
                                            f'</span>'
                                        )
                                    else:
                                        html_weak += (
                                            f'<span style="display:inline-block; text-align:center; margin:5px; vertical-align:top;">'
                                            f'<img src="{b64}" width="56" height="56" title="{elem}"><br>'
                                            f'<span style="font-size:12px;">{elem}</span>'
                                            f'</span>'
                                        )
                                else:
                                    html_weak += f'<span style="margin:5px; font-size:14px; font-weight:bold;">{elem} {tag}</span>' if tag else f'<span style="margin:5px; font-size:14px;">{elem}</span>'
                            st.markdown(html_weak, unsafe_allow_html=True)
                        else:
                            st.write("无")

                # 保存结果文本到 session
                if result_text:
                    st.session_state.last_element_result = result_text
                else:
                    st.session_state.last_element_result = ""