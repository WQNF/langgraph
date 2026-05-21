# frontend/components/number_calculator.py
from frontend.components.NATURE_EFFECTS import NATURE_EFFECTS

STAT_NAMES = ["生命", "攻击", "防御", "魔攻", "魔抗", "速度"]

def find_nature(plus_stat, minus_stat):
    for name, eff in NATURE_EFFECTS.items():
        if eff["+"] == plus_stat and eff["-"] == minus_stat:
            return name
    return None

def get_nature_multipliers(nature_name, star):
    if not nature_name or nature_name not in NATURE_EFFECTS:
        return {s: 1.0 for s in STAT_NAMES}

    effect = NATURE_EFFECTS[nature_name]
    boost_mult = 1.10 + 0.02 * star
    nerf_mult = 0.90

    multipliers = {}
    for s in STAT_NAMES:
        if s == effect["+"]:
            multipliers[s] = boost_mult
        elif s == effect["-"]:
            multipliers[s] = nerf_mult
        else:
            multipliers[s] = 1.0
    return multipliers

def calculate_stats(base_stats, level, star, talents, nature_name):
    # 1. 汇总个体资质
    talent_sum = {s: 0 for s in STAT_NAMES}
    for t in talents:
        talent_sum[t["stat"]] += t["base"] * (star + 1)

    # 2. 性格修正系数
    nature_mult = get_nature_multipliers(nature_name, star)

    # 3. 成长值
    growth = {s: (20 * star) if s == "生命" else (10 * star) for s in STAT_NAMES}

    # 4. 逐项计算
    result = {}
    for stat in STAT_NAMES:
        race = base_stats[stat]
        indi = talent_sum[stat]

        if stat == "生命":
            rate = 1 + race * 0.02 + indi * 0.01
        else:
            rate = race * 0.01 + indi * 0.005

        base_val = 10 + race * 0.5 + indi * 0.25
        final = (base_val + rate * level) * nature_mult[stat] + growth[stat]
        # ---------- 修改部分 ----------
        if final - int(final) == 0.5:
            if stat == "生命":
                result[stat] = int(final) + 1   # 生命 0.5 向上取整
            
            else:
                result[stat] = int(final)       # 其他属性 0.5 向下取整
        else:
            result[stat] = round(final)         # 非 .5 情况四舍五入

    return result

def render_stat_bars(base_stats, talents, star, calc_result, nature_name):
    talent_sum = {s: 0 for s in STAT_NAMES}
    for t in talents:
        talent_sum[t["stat"]] += t["base"] * (star + 1)

    max_width = 210 + 60
    effect = NATURE_EFFECTS.get(nature_name) if nature_name else None
    plus_stat = effect["+"] if effect else None
    minus_stat = effect["-"] if effect else None
    boost_pct = 10 + 2 * star

    # ---- 性格名称显示（新增） ----
    if effect:
        nature_line = f'''
        <div style="font-size:13px; margin-bottom:6px; color:#333;">
            当前性格：<b>{nature_name}</b>（{plus_stat}↑ {minus_stat}↓）
        </div>
        '''
    else:
        nature_line = '<div style="font-size:13px; margin-bottom:6px; color:#999;">当前性格：无修正</div>'

    # 表头
    header = '''
    <div style="display:flex; align-items:center; margin-bottom:4px; font-size:13px; font-weight:bold; color:#666;">
        <span style="width:150px; text-align:left;">属性</span>
        <div style="flex:1;"></div>
        <span style="width:70px; text-align:center;">种族+资质</span>
        <span style="width:50px; text-align:center;">成长</span>
    </div>
    '''

    # 拼接所有行，性格名称在最前
    rows_html = nature_line + header
    for stat in STAT_NAMES:
        race = base_stats[stat]
        indi = talent_sum[stat]
        final_val = calc_result[stat]
        race_pct = (race / max_width) * 100
        indi_pct = (indi / max_width) * 100
        growth = 20 * star if stat == "生命" else 10 * star

        nature_mark = ""
        if stat == plus_stat:
            nature_mark = f'<span style="color:#f5a623; font-weight:bold;">↑{boost_pct}%</span>'
        elif stat == minus_stat:
            nature_mark = f'<span style="color:#e74c3c; font-weight:bold;">↓10%</span>'

        row = f'''
        <div style="display:flex; align-items:center; margin-bottom:5px; font-size:14px; white-space:nowrap;">
            <span style="width:150px; display:flex; align-items:center; justify-content:flex-start;">
                <span style="margin-right:6px;">{stat}</span>
                <span style="font-weight:bold; font-size:16px; color:#000; margin-right:6px;">({final_val})</span>
                <span style="width:45px; text-align:left;">{nature_mark}</span>
            </span>
            <div style="flex:1; height:16px; background:#eee; border-radius:3px; display:flex; margin-left:4px;">
                <div style="width:{race_pct:.1f}%; height:100%; background:#3a7bd5; border-radius:3px 0 0 3px;" title="种族值{race}"></div>
                <div style="width:{indi_pct:.1f}%; height:100%; background:#f5a623; border-radius:0 3px 3px 0;" title="资质{indi}"></div>
            </div>
            <span style="width:70px; text-align:center; margin-left:8px; color:#f5a623;">{race}+{indi}</span>
            <span style="color:#4caf50; width:50px; text-align:center;">+{growth}</span>
        </div>
        '''
        rows_html += row

    return rows_html
