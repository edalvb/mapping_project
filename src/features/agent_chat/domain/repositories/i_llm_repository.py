from abc import ABC, abstractmethod
from typing import Dict

class ILLMRepository(ABC):

    @abstractmethod
    def execute_prompt(self, prompt_template: str, context: Dict[str, str]) -> str:
        pass
