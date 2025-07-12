from typing import Callable, Optional, Set, List

from src.features.project_mapper.domain.models.directory_node_model import DirectoryNode
from src.features.project_mapper.domain.models.mapping_config_model import MappingConfig
from src.features.project_mapper.domain.models.llm_config_model import LLMConfig
from src.features.project_mapper.domain.repositories.i_project_mapper_repository import IProjectMapperRepository
from src.features.project_mapper.domain.repositories.i_llm_repository import I_LLMRepository

class ProjectMapperService:
    def __init__(
        self,
        mapper_repository: IProjectMapperRepository,
        llm_repository: Optional[I_LLMRepository] = None,
    ):
        self._mapper_repository = mapper_repository
        self._llm_repository = llm_repository

    def get_directory_tree(self, path: str) -> Optional[DirectoryNode]:
        return self._mapper_repository.get_directory_tree(path)

    def execute_mapping_to_file(
        self,
        config: MappingConfig,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> int:
        return self._mapper_repository.map_project(config, progress_callback)

    def get_intelligent_folder_selection(
        self,
        llm_config: LLMConfig,
        project_map_content: str,
    ) -> Set[str]:
        if not self._llm_repository:
            raise RuntimeError("LLM repository not configured for this service.")
        
        if not project_map_content.strip():
            raise ValueError("El mapeo del proyecto resultó en contenido vacío.")

        response = self._llm_repository.get_intelligent_selection(
            config=llm_config,
            project_map_content=project_map_content
        )
        return set(response.suggested_paths)

    def get_available_llm_models(self, api_key: str) -> List[str]:
        if not self._llm_repository:
            raise RuntimeError("LLM repository not configured for this service.")
        return self._llm_repository.get_available_models(api_key)