from abc import ABC, abstractmethod
from typing import List

class IProjectMapperRepository(ABC):

    @abstractmethod
    def map_project_to_string(
        self,
        project_dir: str,
        extensions_to_include: List[str],
        extensions_to_exclude: List[str]
    ) -> str:
        pass
