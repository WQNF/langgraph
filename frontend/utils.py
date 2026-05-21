import os
import re
import base64
import streamlit as st

# ---------- 图标路径 ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(BASE_DIR, "data", "elements")
DOC_DIR = os.path.join(BASE_DIR, "data", "documents")

def get_element_icon_base64(element_name: str) -> str:
    """返回属性图标的 base64 编码，用于 HTML 嵌入"""
    if not element_name or element_name == "无":
        return ""
    icon_path = os.path.join(ICON_DIR, f"{element_name}.png")
    if os.path.exists(icon_path):
        try:
            with open(icon_path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
                return f"data:image/png;base64,{data}"
        except Exception:
            return ""
    return ""

# ---------- 单属性克制关系解析 ----------
def parse_single_relations(text: str) -> dict:
    relations = {"我克制": [], "我抵抗": [], "抵抗我": [], "克制我": []}
    element = text.split()[0]  # 取第一个词作为属性名，如“水系”

    # 1. 我克制：水系克制火系，地系，机械系；
    m = re.search(rf'{element}克制(.+?)(?:；|;|$)', text)
    if m:
        relations["我克制"] = [e.strip() for e in re.split(r'[，,、]', m.group(1)) if e.strip()]

    # 2. 我抵抗：水系抵抗火系，机械系；
    m = re.search(rf'{element}抵抗(.+?)(?:；|;|$)', text)
    if m:
        relations["我抵抗"] = [e.strip() for e in re.split(r'[，,、]', m.group(1)) if e.strip()]

    # 3. 抵抗我：草系，冰系，龙系抵抗水系；
    m = re.search(rf'(.+?)抵抗{element}(?:；|;|$)', text)
    if m:
        relations["抵抗我"] = [e.strip() for e in re.split(r'[，,、]', m.group(1)) if e.strip()]

    # 4. 克制我：草系，电系克制水系。
    m = re.search(rf'(.+?)克制{element}(?:；|;|$|。|$)', text)
    if m:
        relations["克制我"] = [e.strip() for e in re.split(r'[，,、]', m.group(1)) if e.strip()]

    return relations

# ---------- 双属性克制关系解析 ----------
def parse_dual_relations(text: str) -> dict:
    result = {"我克制": [], "我抵抗": [], "克制我": []}
    m = re.search(r'我克制：(.+)', text)
    if m:
        off_text = m.group(1)
        skills = re.split(r'[，,](?=\S+系技能)', off_text)
        if len(skills) == 1 and '技能' not in skills[0]:
            skills = [off_text]
        for skill in skills:
            skill = skill.strip()
            if not skill:
                continue
            sm = re.match(r'(\S+系)技能【(.+?)】', skill)
            if sm:
                attr = sm.group(1)
                targets = [x.strip() for x in re.split(r'[、，,]', sm.group(2)) if x.strip()]
                result["我克制"].append((f"{attr}技能克制", targets))
            else:
                simple = [x.strip() for x in re.split(r'[、，,]', skill) if x.strip() and '系' in x]
                if simple:
                    result["我克制"].append(("技能克制", simple))
    m = re.search(r'我抵抗：(.+)', text)
    if m:
        res_text = m.group(1)
        items = [x.strip() for x in re.split(r'[、，,]', res_text) if x.strip()]
        for item in items:
            rm = re.match(r'(\S+系)(?:（(.+?)）)?', item)
            if rm:
                elem = rm.group(1)
                tag = rm.group(2) if rm.group(2) else ""
                result["我抵抗"].append((elem, tag))
            else:
                result["我抵抗"].append((item, ""))
    m = re.search(r'克制我：(.+)', text)
    if m:
        weak_text = m.group(1)
        items = [x.strip() for x in re.split(r'[、，,]', weak_text) if x.strip()]
        for item in items:
            rm = re.match(r'(\S+系)(?:（(.+?)）)?', item)
            if rm:
                elem = rm.group(1)
                tag = rm.group(2) if rm.group(2) else ""
                result["克制我"].append((elem, tag))
            else:
                result["克制我"].append((item, ""))
    return result

# ---------- 加载本地文档 ----------
def parse_single_type_dict(text: str) -> dict:
    result = {}
    parts = re.split(r'\d+、', text)[1:]
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.split('\n', 1)
        if len(lines) >= 1:
            element_name = lines[0].strip()
            result[element_name] = part
    return result

def parse_dual_type_dict(text: str) -> dict:
    result = {}
    parts = re.split(r'\d+、', text)[1:]
    for part in parts:
        part = part.strip()
        if not part:
            continue
        match = re.search(r'(\S+系)\+(\S+系)', part)
        if match:
            combo = f"{match.group(1)}+{match.group(2)}"
            result[combo] = part
    return result

def load_element_data():
    """返回 (single_data, dual_data) 字典"""
    single_data, dual_data = {}, {}
    try:
        single_path = os.path.join(DOC_DIR, "单属性克制表.txt")
        dual_path = os.path.join(DOC_DIR, "双属性克制表.txt")
        if os.path.exists(single_path):
            with open(single_path, "r", encoding="utf-8") as f:
                single_data = parse_single_type_dict(f.read())
        if os.path.exists(dual_path):
            with open(dual_path, "r", encoding="utf-8") as f:
                dual_data = parse_dual_type_dict(f.read())
    except Exception as e:
        st.warning(f"加载属性文档失败: {e}")
    return single_data, dual_data