"""Base Agent基类"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLLM


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(
        self,
        name: str,
        description: str,
        llm: Optional[BaseLLM] = None,
        prompt: Optional[ChatPromptTemplate] = None
    ):
        """
        初始化Agent
        
        Args:
            name: Agent名称
            description: Agent描述
            llm: 语言模型
            prompt: 提示模板
        """
        self.name = name
        self.description = description
        self.llm = llm
        self.prompt = prompt
        self.memory: Dict[str, Any] = {}
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Agent任务
        
        Args:
            input_data: 输入数据
            
        Returns:
            Dict: 执行结果
        """
        pass
    
    def update_memory(self, key: str, value: Any) -> None:
        """更新内存"""
        self.memory[key] = value
    
    def get_memory(self, key: str) -> Any:
        """获取内存"""
        return self.memory.get(key)
    
    def clear_memory(self) -> None:
        """清空内存"""
        self.memory.clear()
