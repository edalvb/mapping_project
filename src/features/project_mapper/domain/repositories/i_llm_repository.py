from abc import ABC, abstractmethod
from typing import List

from src.features.project_mapper.domain.models.llm_config_model import LLMConfig
from src.features.project_mapper.domain.models.llm_response_model import LLMSuggestionResponse

class I_LLMRepository(ABC):
    @abstractmethod
    def get_available_models(self, api_key: str) -> List[str]:
        pass

    @abstractmethod
    def get_intelligent_selection(
        self, config: LLMConfig, project_map_content: str
    ) -> LLMSuggestionResponse:
        pass