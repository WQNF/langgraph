from abc import ABC, abstractmethod
from typing import List, Callable, Dict, Any

class BaseSkill(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def get_prompt(self) -> str:
        """返回该技能的专属系统提示词"""
        pass

    @abstractmethod
    def get_tools(self) -> List[Callable]:
        """返回该技能所需的工具函数列表（当前洛克王国助手不使用工具，可返回空列表）"""
        pass

    @abstractmethod
    def get_resources(self) -> List[Dict[str, Any]]:
        """返回该技能需要的资源描述（如知识库索引名等）"""
        pass

    def activate(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "prompt": self.get_prompt(),
            "tools": self.get_tools(),
            "resources": self.get_resources()
        }