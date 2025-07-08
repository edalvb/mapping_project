from abc import ABC, abstractmethod
from typing import Callable, Optional, List

from src.features.project_mapper.domain.models.mapping_config_model import MappingConfig

class IProjectMapperRepository(ABC):
    @abstractmethod
    def get_subdirectories(self, path: str) -> List[str]:
        pass

    @abstractmethod
    def map_project(
        self, 
        config: MappingConfig, 
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> int:
        pass
