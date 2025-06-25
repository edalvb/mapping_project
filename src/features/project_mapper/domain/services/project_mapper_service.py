from typing import Callable, Optional
from src.features.project_mapper.domain.repositories.i_project_mapper_repository import IProjectMapperRepository
from src.features.project_mapper.domain.models.mapping_config_model import MappingConfig

class ProjectMapperService:
    def __init__(self, repository: IProjectMapperRepository):
        self._repository = repository

    def execute(
        self, 
        config: MappingConfig, 
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> int:
        return self._repository.map_project(config, progress_callback)