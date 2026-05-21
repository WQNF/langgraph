import streamlit as st
import httpx
from frontend.components.number_calculator import (
    STAT_NAMES,
    NATURE_EFFECTS,
    find_nature,
    calculate_stats,
)
from frontend.components.extreme_damage_button import (
    _calc_damage, _render_hp_bar, render_extreme_damage_analysis
)

def _render_hp_bar(current_hp, max_hp):
    """生成横向血条 HTML，剩余血量绿色，损失血量黄色，中间显示剩余百分比"""
    if max_hp <= 0:
        return ""
    pct_remaining = current_hp / max_hp
    pct_lost = 1 - pct_remaining
    bar_html = f'''
    <div style="margin:4px 0; font-size:14px;">
        <div style="display:inline-block; width:calc(100% - 70px); height:20px; background:#f0a500; border-radius:4px; position:relative;">
            <div style="width:{pct_remaining:.1%}; height:100%; background:#4caf50; border-radius:4px 0 0 4px; position:absolute; left:0; top:0;"></div>
            <span style="position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); font-weight:bold; color:#fff; text-shadow:1px 1px 2px #000; white-space:nowrap;">
                {current_hp}/{max_hp} ({pct_remaining:.0%})
            </span>
        </div>
    </div>
    '''
    return bar_html

# ---------- 精灵数据缓存 ----------
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

# ---------- 伤害计算器主入口 ----------
def render_damage_calculator_sidebar():
    if st.session_state.get("streaming", False):
        st.info("⏳ 聊天进行中，计算器暂不可用")
        return

    # 初始化攻击方/防御方状态（能力值 + 技能参数）
    for side in ["atk", "def"]:
        defaults = {
            f"dmg_{side}_pokemon_name": "",
            f"dmg_{side}_base_stats": {s: 100 for s in STAT_NAMES},
            f"dmg_{side}_level": 60,
            f"dmg_{side}_nature": "固执",
            f"dmg_{side}_plus_stat": "攻击",
            f"dmg_{side}_minus_stat": "魔攻",
            f"dmg_{side}_star": 5,
            f"dmg_{side}_talents": {},
            f"dmg_{side}_final_stats": None,
            # 技能参数
            f"dmg_{side}_skill_power": 80,
            f"dmg_{side}_move_type": "物理",
            f"dmg_{side}_combo": 1,
            f"dmg_{side}_reduction": 0,
        }
        for key, val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = val

    star = 5

    with st.sidebar:
        with st.expander("⚔️ 伤害计算器", expanded=True):
            if st.button("✖️ 关闭", key="close_dmg_calc"):
                st.session_state.show_damage_calculator = False
                st.rerun()

            st.caption(f"当前星级：⭐⭐⭐⭐⭐ (5星，等级60)")

            col_atk, col_def = st.columns(2)

            with col_atk:
                st.markdown("**🗡️ 攻击方**")
                _render_pokemon_card("atk", star)

            with col_def:
                st.markdown("**🛡️ 防御方**")
                _render_pokemon_card("def", star)

            st.divider()

            # 计算双方伤害
            with st.expander("🧮 计算双方伤害",expanded=False):
                if st.button("✖️ 关闭", key="_calc_damage"):
                    st.session_state.show_damage_calculator = False
                    st.rerun()
                atk_stats = st.session_state.get("dmg_atk_final_stats")
                def_stats = st.session_state.get("dmg_def_final_stats")

                if not atk_stats or not def_stats:
                    st.error("请先在双方卡片中填写完整的参数（性格、资质）")
                else:
                    # 攻击方 → 防御方
                    if st.session_state.dmg_atk_move_type == "物理":
                        atk_attack = atk_stats["攻击"]
                        def_defense = def_stats["防御"]
                    else:
                        atk_attack = atk_stats["魔攻"]
                        def_defense = def_stats["魔抗"]

                    dmg1 = _calc_damage(
                        attack=atk_attack,
                        defense=def_defense,
                        power=st.session_state.dmg_atk_skill_power,
                        combo=st.session_state.dmg_atk_combo,
                        reduction=st.session_state.dmg_atk_reduction
                    )

                    # 防御方 → 攻击方
                    if st.session_state.dmg_def_move_type == "物理":
                        def_attack = def_stats["攻击"]
                        atk_defense = atk_stats["防御"]
                    else:
                        def_attack = def_stats["魔攻"]
                        atk_defense = atk_stats["魔抗"]

                    dmg2 = _calc_damage(
                        attack=def_attack,
                        defense=atk_defense,
                        power=st.session_state.dmg_def_skill_power,
                        combo=st.session_state.dmg_def_combo,
                        reduction=st.session_state.dmg_def_reduction
                    )

                    # 伤害计算后显示伤害和血条
                    # 攻击方生命（被防御方打后的剩余）
                    atk_max_hp = atk_stats["生命"]
                    atk_remaining = max(1, atk_max_hp - dmg2)  # 不能被防御方一击打死？可由用户自行判断，这里展示剩余
                    # 防御方生命（被攻击方打后的剩余）
                    def_max_hp = def_stats["生命"]
                    def_remaining = max(1, def_max_hp - dmg1)

                    atk_name = st.session_state.get("dmg_atk_pokemon_name", "攻击方")
                    def_name = st.session_state.get("dmg_def_pokemon_name", "防御方")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{atk_name} → {def_name}**")
                        st.metric("造成伤害", dmg1)
                        st.html(_render_hp_bar(def_remaining, def_max_hp))

                    with col2:
                        st.markdown(f"**{def_name} → {atk_name}**")
                        st.metric("造成伤害", dmg2)
                        st.html(_render_hp_bar(atk_remaining, atk_max_hp))
            render_extreme_damage_analysis()

def _calc_damage(attack, defense, power, combo, reduction):
    """基础伤害公式"""
    damage = (attack / defense) * 0.9 * power * combo * (1 - reduction / 100)
    return max(1, int(int(damage)))

# ---------- 精灵卡片渲染 ----------
def _render_pokemon_card(side, star):
    """渲染一个精灵卡片，包含配置和技能参数"""
    prefix = f"dmg_{side}"

    # 1. 精灵选择
    pokemon_list = fetch_pokemon_list()
    if pokemon_list:
        options = {f"{p['national_number']} - {p['name']}": p for p in pokemon_list}
        selected_label = st.selectbox(
            "选择精灵",
            ["— 不选择 —"] + list(options.keys()),
            key=f"{prefix}_select"
        )
        if selected_label != "— 不选择 —":
            pokemon = options[selected_label]
            detail = fetch_pokemon_detail(pokemon["id"])
            if detail and "stats" in detail:
                new_stats = {
                    "生命": detail["stats"]["hp"],
                    "攻击": detail["stats"]["attack"],
                    "防御": detail["stats"]["defense"],
                    "魔攻": detail["stats"]["sp_attack"],
                    "魔抗": detail["stats"]["sp_defense"],
                    "速度": detail["stats"]["speed"]
                }
                if new_stats != st.session_state[f"{prefix}_base_stats"]:
                    st.session_state[f"{prefix}_base_stats"] = new_stats
                    st.session_state[f"{prefix}_pokemon_name"] = detail["name"]
                    st.rerun()

    # 2. 性格
    st.markdown("**性格**")
    col_plus, col_minus = st.columns(2)
    with col_plus:
        plus_stat = st.selectbox(
            "增加属性", STAT_NAMES,
            index=STAT_NAMES.index(st.session_state[f"{prefix}_plus_stat"]),
            key=f"{prefix}_plus"
        )
    with col_minus:
        minus_stat = st.selectbox(
            "减少属性", STAT_NAMES,
            index=STAT_NAMES.index(st.session_state[f"{prefix}_minus_stat"]),
            key=f"{prefix}_minus"
        )

    if (plus_stat != st.session_state[f"{prefix}_plus_stat"] or
            minus_stat != st.session_state[f"{prefix}_minus_stat"]):
        st.session_state[f"{prefix}_plus_stat"] = plus_stat
        st.session_state[f"{prefix}_minus_stat"] = minus_stat
        nature_name = find_nature(plus_stat, minus_stat)
        st.session_state[f"{prefix}_nature"] = nature_name if nature_name else "无修正"
        st.rerun()

    if st.session_state[f"{prefix}_nature"]:
        st.caption(f"性格: {st.session_state[f'{prefix}_nature']} ({plus_stat}↑ {minus_stat}↓)")
    else:
        st.caption("无匹配性格")

    # 3. 资质（折叠，默认收起）
    with st.expander("📊 资质", expanded=False):
        st.caption("勾选有资质的属性 (最多3个)")
        current_talents = st.session_state.get(f"{prefix}_talents", {})
        talents = {}
        checked_count = len(current_talents)

        for stat in STAT_NAMES:
            check_key = f"{prefix}_talent_{stat}_check"
            val_key = f"{prefix}_talent_{stat}_val"

            default_checked = stat in current_talents
            disabled = (checked_count >= 3 and not default_checked)

            col1, col2 = st.columns([1, 3])
            with col1:
                checked = st.checkbox(stat, value=default_checked, disabled=disabled, key=check_key)
            with col2:
                if checked:
                    val = st.number_input(
                        f"{stat}基础值", min_value=7, max_value=10,
                        value=current_talents.get(stat, 7), key=val_key
                    )
                    talents[stat] = val
                else:
                    st.number_input(
                        f"{stat}基础值", min_value=7, max_value=10,
                        value=7, disabled=True, key=val_key
                    )

        st.session_state[f"{prefix}_talents"] = talents

    # 4. 种族值（折叠，默认收起）
    with st.expander("📊 种族值", expanded=False):
        base = st.session_state[f"{prefix}_base_stats"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("生命", base["生命"])
        with col2:
            st.metric("攻击", base["攻击"])
        with col3:
            st.metric("防御", base["防御"])
        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("魔攻", base["魔攻"])
        with col5:
            st.metric("魔抗", base["魔抗"])
        with col6:
            st.metric("速度", base["速度"])

    # 5. 最终能力值（折叠，默认收起）
    base = st.session_state[f"{prefix}_base_stats"]
    nature = st.session_state[f"{prefix}_nature"]
    if nature == "无修正":
        nature = None
    talents_list = [{"stat": s, "base": v} for s, v in talents.items()]

    final_stats = calculate_stats(
        base_stats=base,
        level=st.session_state[f"{prefix}_level"],
        star=star,
        talents=talents_list,
        nature_name=nature
    )
    st.session_state[f"{prefix}_final_stats"] = final_stats

    with st.expander("📈 最终能力值", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("生命", final_stats["生命"])
        with col2:
            st.metric("攻击", final_stats["攻击"])
        with col3:
            st.metric("防御", final_stats["防御"])
        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("魔攻", final_stats["魔攻"])
        with col5:
            st.metric("魔抗", final_stats["魔抗"])
        with col6:
            st.metric("速度", final_stats["速度"])
    # 6. 技能参数（折叠，默认展开）
    with st.expander("⚡ 技能参数", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.number_input(
                "技能威力", min_value=1,
                value=st.session_state[f"{prefix}_skill_power"],
                key=f"{prefix}_skill_power"
            )
        with col2:
            st.selectbox(
                "技能类型", ["物理", "特殊"],
                index=["物理", "特殊"].index(st.session_state[f"{prefix}_move_type"]),
                key=f"{prefix}_move_type"
            )
        col3, col4 = st.columns(2)
        with col3:
            st.number_input(
                "连击数", min_value=1,
                value=st.session_state[f"{prefix}_combo"],
                key=f"{prefix}_combo"
            )
        with col4:
            st.number_input(
                "减伤 (%)", min_value=0, max_value=100,
                value=st.session_state[f"{prefix}_reduction"],
                key=f"{prefix}_reduction"
            )