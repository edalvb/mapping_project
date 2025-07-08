from abc import ABC, abstractmethod
from typing import Callable, Optional

from src.features.project_mapper.domain.models.mapping_config_model import MappingConfig
from src.features.project_mapper.domain.models.directory_node_model import DirectoryNode

class IProjectMapperRepository(ABC):
    @abstractmethod
    def get_directory_tree(self, path: str) -> Optional[DirectoryNode]:
        pass

    @abstractmethod
    def map_project(
        self, 
        config: MappingConfig, 
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> int:
        pass