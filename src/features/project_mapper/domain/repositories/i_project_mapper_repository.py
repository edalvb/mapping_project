from abc import ABC, abstractmethod
from typing import Callable, Optional

from src.features.project_mapper.domain.models.mapping_config_model import MappingConfig

class IProjectMapperRepository(ABC):
    @abstractmethod
    def map_project(
        self, 
        config: MappingConfig, 
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> int:
        pass