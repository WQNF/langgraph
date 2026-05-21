from skills.base import BaseSkill

class TypeAnalysisSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="type_analysis",
            description="分析属性的克制/被克/抵抗关系，或双属性精灵的属性组合"
        )

    def get_prompt(self) -> str:
        return (
            "你是《洛克王国》属性对战分析师。请严格依据下面提供的【属性克制表文档】，"
            "对用户指定的属性或双属性精灵进行克制面、被克制面、抵抗面、被抵抗面分析。"
            "所有系别名称必须来自文档，禁止编造。"
            "分析时需考虑单属性技能攻击双属性目标时的倍率关系。"
            "-强力克制：造成3倍伤害。"
            "-强力抵抗：造成1/3倍伤害。"
            "请按以下结构输出：\n"
            "1. 输出能力（能打出多少伤害？）\n"
            "2. 生存能力（谁会对我造成高伤害？）\n"
            "3. 联防价值简评\n"
            "报告中应清晰列出各系别及其倍率关系。"
        )

    def get_tools(self) -> list:
        return []

    def get_resources(self) -> list:
        return [{"uri": "knowledge://type_chart", "description": "属性克制表文档"}]