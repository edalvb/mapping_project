from typing import Callable, Optional
from src.features.project_mapper.domain.repositories.i_project_mapper_repository import IProjectMapperRepository
from src.features.project_mapper.domain.models.mapping_config_model import MappingConfig
from src.features.project_mapper.domain.models.directory_node_model import DirectoryNode

class ProjectMapperService:
    def __init__(self, repository: IProjectMapperRepository):
        self._repository = repository

    def get_directory_tree(self, path: str) -> Optional[DirectoryNode]:
        return self._repository.get_directory_tree(path)

    def execute(
        self, 
        config: MappingConfig, 
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> int:
        return self._repository.map_project(config, progress_callback)