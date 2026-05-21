import streamlit as st
import math
from frontend.components.number_calculator import (
    STAT_NAMES,
    NATURE_EFFECTS,
    calculate_stats,
)

def _calc_damage(attack, defense, power, combo, reduction):
    damage = (attack / defense) * 0.9 * power * combo * (1 - reduction / 100)
    return max(1, int(damage))


def _calc_required_power(attack, defense, target_hp, combo, reduction):
    # 计算造成指定伤害所需的技能威力
    required_damage = target_hp  # 要秒杀对手，需要造成的伤害等于对方血量
    power_needed = (required_damage * defense) / (attack * 0.9 * combo * (1 - reduction / 100))
    return max(0, power_needed)


def _render_hp_bar(current_hp, max_hp):
    if max_hp <= 0:
        return ""
    pct = current_hp / max_hp
    return f'''<div style="margin:4px 0; font-size:14px;">
        <div style="display:inline-block; width:100%; height:20px; background:#f0a500; border-radius:4px; position:relative;">
            <div style="width:{pct:.1%}; height:100%; background:#4caf50; border-radius:4px; position:absolute; left:0; top:0;"></div>
            <span style="position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); font-weight:bold; color:#fff; text-shadow:1px 1px 2px #000;">
                {current_hp}/{max_hp} ({pct:.0%})
            </span>
        </div>
    </div>'''


def render_extreme_damage_analysis():
    if not st.session_state.get("dmg_atk_final_stats") or not st.session_state.get("dmg_def_base_stats"):
        st.info("请先在主界面配置攻击方和防御方")
        return

    atk_stats = st.session_state.dmg_atk_final_stats
    def_stats = st.session_state.dmg_def_final_stats
    
    move_type = st.session_state.dmg_atk_move_type
    attack_val = atk_stats["攻击"] if move_type == "物理" else atk_stats["魔攻"]
    def_base = st.session_state.dmg_def_base_stats
    def_name = st.session_state.get("dmg_def_pokemon_name", "防御方")
    combo = st.session_state.dmg_atk_combo
    reduction = st.session_state.dmg_atk_reduction

    with st.expander("📊 极限伤害分析", expanded=False):
        col_atk, col_def = st.columns(2)
        with col_atk:
            with st.expander("📈 攻击方最终能力值", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("生命", atk_stats["生命"])
                with col2:
                    st.metric("攻击", atk_stats["攻击"])
                with col3:
                    st.metric("防御", atk_stats["防御"])
                col4, col5, col6 = st.columns(3)
                with col4:
                    st.metric("魔攻", atk_stats["魔攻"])
                with col5:
                    st.metric("魔抗", atk_stats["魔抗"])
                with col6:
                    st.metric("速度", atk_stats["速度"])
        with col_def:
            with st.expander("📈 防御方最终能力值", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("生命", def_stats["生命"])
                with col2:
                    st.metric("攻击", def_stats["攻击"])
                with col3:
                    st.metric("防御", def_stats["防御"])
                col4, col5, col6 = st.columns(3)
                with col4:
                    st.metric("魔攻", def_stats["魔攻"])
                with col5:
                    st.metric("魔抗", def_stats["魔抗"])
                with col6:
                    st.metric("速度", def_stats["速度"])
        
        # 计算秒杀所需技能威力
        with st.expander("💥 秒杀威力计算", expanded=True):
            # 物理攻击计算：攻击 vs 防御
            phys_attack = atk_stats["攻击"]
            phys_defense = def_stats["防御"]
            phys_power_needed = _calc_required_power(phys_attack, phys_defense, def_stats["生命"], combo, reduction)
            
            # 魔法攻击计算：魔攻 vs 魔抗
            mag_attack = atk_stats["魔攻"]
            mag_defense = def_stats["魔抗"]
            mag_power_needed = _calc_required_power(mag_attack, mag_defense, def_stats["生命"], combo, reduction)
            
            st.subheader(f"需要的技能威力以秒杀 {def_name}")
            
            col_phys, col_mag = st.columns(2)
            with col_phys:
                st.markdown(f"### 🔴 物理攻击")
                st.metric(label="所需威力", value=f"{phys_power_needed:.2f}")
                st.progress(min(1.0, phys_power_needed / 200.0), text=f"物理攻击需 {phys_power_needed:.2f} 威力")
                
            with col_mag:
                st.markdown(f"### 🔵 魔法攻击")
                st.metric(label="所需威力", value=f"{mag_power_needed:.2f}")
                st.progress(min(1.0, mag_power_needed / 200.0), text=f"魔法攻击需 {mag_power_needed:.2f} 威力")
            
            # 显示当前选择的攻击类型所需威力
            current_power_needed = phys_power_needed if move_type == "物理" else mag_power_needed
            st.markdown(f"### ⚔️ 当前攻击类型（{move_type}）需要威力: {current_power_needed:.2f}")
            
            # 提供额外信息
            st.info(f"提示: 攻击方 {st.session_state.get('dmg_atk_pokemon_name', '攻击方')} 的 {move_type} 攻击为 {attack_val}, 对手 {def_name} 的 {move_type} 防御为 {phys_defense if move_type == '物理' else mag_defense}, 生命值为 {def_stats['生命']}")