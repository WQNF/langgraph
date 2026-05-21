from skills.base import BaseSkill

class TeamSynergySkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="team_synergy",
            description="分析多只精灵组成的队伍联防效果、弱点覆盖、打击面等"
        )

    def get_prompt(self) -> str:
        return (
            "你是一位顶级的洛克王国队伍构建师。请根据提供的队伍精灵数据（属性、种族值）以及属性克制表文档，"
            "综合分析整支队伍的联防能力。重点关注：\n"
            "- 全队共同弱点（强力抵抗）\n"
            "- 抵抗面盲区（缺少抵抗的系别）\n"
            "- 打击面覆盖是否全面（强力克制）\n"
            "- 队伍缺少的功能（如特盾、物盾、高速收割等）\n"
            "- 给出替换或补充精灵的建议\n"
            "所有分析必须基于克制表文档，禁止编造属性关系。"
        )

    def get_tools(self) -> list:
        return []

    def get_resources(self) -> list:
        return [{"uri": "knowledge://type_chart", "description": "属性克制表文档"}]