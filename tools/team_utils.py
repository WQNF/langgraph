# tools/team_utils.py
"""团队分析辅助函数"""
import json
from core.llm import llm

def extract_weaknesses_from_analysis(analysis_text: str) -> list:
    """从第一次分析文本中提取弱点属性，返回属性列表如 ["火系", "电系"]"""
    print("\n【extract_weaknesses_from_analysis】开始提取弱点属性")
    print(f"  分析文本长度: {len(analysis_text)} 字符")
    
    prompt = f"""从以下队伍分析报告中，提取所有被提到的弱点属性（如"火系"、"电系"等），只返回 JSON 数组，例如 ["火系","电系"]。

报告内容：
{analysis_text[:2000]}

弱点属性数组："""

    resp = llm.invoke(prompt)
    content = resp.content.strip()
    print(f"  LLM返回的原始内容: {content[:200]}...")
    
    try:
        weaknesses = json.loads(content)
        if isinstance(weaknesses, list):
            print(f"【extract_weaknesses_from_analysis】成功提取弱点: {weaknesses}")
            return weaknesses
    except json.JSONDecodeError:
        print(f"  JSON解析失败，原始内容: {content}")
    
    print("【extract_weaknesses_from_analysis】提取失败，返回空列表")
    return []