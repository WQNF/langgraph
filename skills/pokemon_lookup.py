from skills.base import BaseSkill

class PokemonLookupSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="pokemon_lookup",
            description="查询精灵的种族值、属性、特性等基础信息"
        )

    def get_prompt(self) -> str:
        return (
            "你是一个专业的洛克王国精灵图鉴助手。请根据数据库查询结果，"
            "准确回答用户关于精灵的名称、编号、属性、种族值、特性等问题。"
            "如果数据库中没有该精灵，请明确说明未收录。"
            "不要添加任何游戏内未证实的信息。"
        )

    def get_tools(self) -> list:
        # 当前精灵查询由 pokemon_agent 完成，不需要额外工具
        return []

    def get_resources(self) -> list:
        return [{"uri": "db://pokemon", "description": "精灵数据库"}]