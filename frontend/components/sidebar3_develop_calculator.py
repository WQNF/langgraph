import streamlit as st
import httpx
from frontend.components.number_calculator import (
    STAT_NAMES,
    NATURE_EFFECTS,
    find_nature,
    calculate_stats,
    render_stat_bars,

)

# ---------- 性格数据 ----------


STAT_NAMES = ["生命", "攻击", "防御", "魔攻", "魔抗", "速度"]

def find_nature(plus_stat, minus_stat):
    for name, eff in NATURE_EFFECTS.items():
        if eff["+"] == plus_stat and eff["-"] == minus_stat:
            return name
    return None

def render_calculator_sidebar():
    if st.session_state.get("streaming", False):
        st.info("⏳ 聊天进行中，计算器暂不可用")
        return

    # 初始化 session_state
    defaults = {
        "calc_pokemon_name": "",
        "calc_base_stats": {"生命": 100, "攻击": 100, "防御": 100,
                            "魔攻": 100, "魔抗": 100, "速度": 100},
        "calc_level": 50,
        "calc_nature": "开朗",
        "calc_plus_stat": "速度",
        "calc_minus_stat": "魔攻",
        "calc_star": 0,
        "calc_talent_count": 1,
        "calc_talents": [{"stat": "攻击", "base": 7}],
        "calc_result": None,
        "show_calculator": True,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    with st.sidebar:
        with st.expander("⚔️ 精灵培养计算器", expanded=True):
            
            st.markdown(
            "<h2 style='text-align: center;'>⚔️ 精灵培养计算器 </h2>",
            unsafe_allow_html=True
        )
        # ---------- 关闭按钮 ----------
            if st.button("✖️ 关闭", key="close_develop_calc"):
                st.session_state.show_calculator = False
                st.rerun()

            # ===== 1. 精灵选择（自动填充，无手动输入） =====

            with st.expander("🔍 精灵选择", expanded=True):
                try:
                    resp = httpx.get("http://127.0.0.1:8000/pokemons", timeout=10)
                    if resp.status_code == 200:
                        pokemon_list = resp.json()
                    else:
                        pokemon_list = []
                except Exception:
                    pokemon_list = []

                if pokemon_list:
                    options = {f"{p['national_number']} - {p['name']}": p for p in pokemon_list}
                    all_options = ["— 默认种族值 —"] + list(options.keys())
                    selected_label = st.selectbox(
                        "选择精灵（自动填充种族值）",
                        all_options,
                        key="auto_fill_select"
                    )

                    if selected_label == "— 默认种族值 —":
                        default_stats = {"生命": 100, "攻击": 100, "防御": 100,
                                        "魔攻": 100, "魔抗": 100, "速度": 100}
                        if st.session_state.calc_base_stats != default_stats:
                            st.session_state.calc_base_stats = default_stats
                            st.session_state.calc_pokemon_name = ""
                            st.rerun()
                    else:
                        selected_pokemon = options[selected_label]
                        pid = selected_pokemon["id"]
                        try:
                            resp2 = httpx.get(f"http://127.0.0.1:8000/pokemon/{pid}", timeout=10)
                            if resp2.status_code == 200:
                                detail = resp2.json()
                            else:
                                detail = None
                        except Exception:
                            detail = None

                        if detail is None:
                            st.warning("⚠️ 无法获取精灵详细信息")
                        elif "stats" not in detail:
                            st.warning("⚠️ 缺少种族值数据")
                        else:
                            new_stats = {
                                "生命": detail["stats"]["hp"],
                                "攻击": detail["stats"]["attack"],
                                "防御": detail["stats"]["defense"],
                                "魔攻": detail["stats"]["sp_attack"],
                                "魔抗": detail["stats"]["sp_defense"],
                                "速度": detail["stats"]["speed"]
                            }
                            if new_stats != st.session_state.calc_base_stats:
                                st.session_state.calc_base_stats = new_stats
                                st.session_state.calc_pokemon_name = detail["name"]
                                st.rerun()
                else:
                    st.warning("⚠️ 无法获取精灵列表，请确认后端已启动")
                # ---- 显示当前种族值（只读） ----
                # 显示当前种族值（两行三列，小字体）
                # 显示当前种族值（两行三列，适中字体，附总和）
                base = st.session_state.calc_base_stats
                total = sum(base.values())
                st.markdown(f"**当前种族值**  (总和: **{total}**)")

                row1 = st.columns(3)
                with row1[0]:
                    st.write(f"生命: {base['生命']}")
                with row1[1]:
                    st.write(f"攻击: {base['攻击']}")
                with row1[2]:
                    st.write(f"防御: {base['防御']}")
                row2 = st.columns(3)
                with row2[0]:
                    st.write(f"魔攻: {base['魔攻']}")
                with row2[1]:
                    st.write(f"魔抗: {base['魔抗']}")
                with row2[2]:
                    st.write(f"速度: {base['速度']}")

            #st.divider()

            # ===== 2. 培养参数 =====
            with st.expander("📊 培养参数", expanded=True):
                col_lv, col_star = st.columns(2)
                with col_lv:
                    st.markdown("**等级**")
                    level = st.number_input(
                        "等级", min_value=1, max_value=60,
                        value=st.session_state.calc_level,
                        key="level_input", label_visibility="collapsed"
                    )
                    if level != st.session_state.calc_level:
                        st.session_state.calc_level = level

                with col_star:
                    st.markdown("**星级**")
                    star = st.session_state.calc_star
                    star_cols = st.columns(5)
                    for i in range(5):
                        with star_cols[i]:
                            icon = "⭐" if i < star else "☆"
                            if st.button(icon, key=f"star_{i}"):
                                new_star = i if star > i else i + 1
                                st.session_state.calc_star = new_star
                                st.rerun()
                    growth_hp = 20 * star
                    growth_other = 10 * star
                    st.caption(f"当前星级: {star}  \n  生命成长 +{growth_hp}，其他五项 +{growth_other}")

                #st.divider()

                # 性格
                st.markdown("**性格**")
                col_plus, col_minus = st.columns(2)
                with col_plus:
                    plus_stat = st.selectbox(
                        "增加属性", STAT_NAMES,
                        index=STAT_NAMES.index(st.session_state.calc_plus_stat),
                        key="plus_stat_select"
                    )
                with col_minus:
                    minus_stat = st.selectbox(
                        "减少属性", STAT_NAMES,
                        index=STAT_NAMES.index(st.session_state.calc_minus_stat),
                        key="minus_stat_select"
                    )

                if (plus_stat != st.session_state.calc_plus_stat or
                        minus_stat != st.session_state.calc_minus_stat):
                    st.session_state.calc_plus_stat = plus_stat
                    st.session_state.calc_minus_stat = minus_stat
                    nature_name = find_nature(plus_stat, minus_stat)
                    st.session_state.calc_nature = nature_name if nature_name else None
                    st.rerun()

                if st.session_state.calc_nature:
                    st.success(
                        f"匹配性格: {st.session_state.calc_nature} "
                        f"({st.session_state.calc_plus_stat}↑ {st.session_state.calc_minus_stat}↓)"
                    )
                else:
                    st.error("无匹配性格，请检查增减组合")

                #st.divider()

                # 资质
                st.markdown("**资质 (1~3条)**")
                talent_count = st.selectbox(
                    "资质条数", [1, 2, 3],
                    index=st.session_state.calc_talent_count - 1,
                    key="talent_count"
                )
                if talent_count != st.session_state.calc_talent_count:
                    st.session_state.calc_talent_count = talent_count
                    cur = st.session_state.calc_talents
                    while len(cur) < talent_count:
                        cur.append({"stat": "攻击", "base": 7})
                    while len(cur) > talent_count:
                        cur.pop()
                    st.session_state.calc_talents = cur

                talents = st.session_state.calc_talents
                for i in range(talent_count):
                    col_sel, col_val = st.columns([3, 2])
                    with col_sel:
                        chosen = st.selectbox(
                            f"资质{i+1}属性", STAT_NAMES,
                            index=STAT_NAMES.index(talents[i]["stat"]) if talents[i]["stat"] in STAT_NAMES else 0,
                            key=f"talent_stat_{i}"
                        )
                        talents[i]["stat"] = chosen
                    with col_val:
                        base_val = st.number_input(
                            "基础值", min_value=7, max_value=10,
                            value=talents[i]["base"],
                            key=f"talent_base_{i}"
                        )
                        talents[i]["base"] = base_val
                    bonus = base_val * (st.session_state.calc_star + 1)
                    st.caption(f"→ 当前加成: {talents[i]['stat']} +{bonus}")

            #st.divider()

            # ===== 3. 计算结果 =====
            with st.expander("📈 计算结果", expanded=True):
                if st.button("🧮 计算最终能力值", key="calc_button"):
                    result = calculate_stats(
                        base_stats=st.session_state.calc_base_stats,
                        level=st.session_state.calc_level,
                        star=st.session_state.calc_star,
                        talents=st.session_state.calc_talents,
                        nature_name=st.session_state.calc_nature
                    )
                    st.session_state.calc_result = result

                if st.session_state.calc_result:
                    # 顶部行：标题 + 雷达图切换按钮
                    col_title, col_btn = st.columns([5, 1])
                    with col_title:
                        st.markdown("**能力值详情**")
                    with col_btn:
                        if st.button("🔍", key="toggle_radar", help="显示/隐藏六维雷达图"):
                            st.session_state.show_radar = not st.session_state.show_radar
                            st.rerun()

                    # 横向条形图
                    html = render_stat_bars(
                        base_stats=st.session_state.calc_base_stats,
                        talents=st.session_state.calc_talents,
                        star=st.session_state.calc_star,
                        calc_result=st.session_state.calc_result,
                        nature_name=st.session_state.calc_nature
                    )
                    st.html(html)


            st.divider()

            # ===== 底部按钮 =====
            col_copy, col_reset_bottom = st.columns(2)
            with col_copy:
                if st.button("📋 复制结果"):
                    if st.session_state.calc_result:
                        lines = [f"{k}: {v}" for k, v in st.session_state.calc_result.items()]
                        st.code("\n".join(lines), language="text")
                        st.success("结果已显示在上方代码块，可手动复制")
                    else:
                        st.warning("请先点击计算")
            with col_reset_bottom:
                if st.button("🔄 恢复默认", key="reset_bottom"):
                    st.session_state.calc_star = 0
                    st.session_state.calc_plus_stat = "速度"
                    st.session_state.calc_minus_stat = "魔攻"
                    st.session_state.calc_nature = "开朗"
                    st.rerun()