from abc import ABC, abstractmethod
from typing import List

from src.features.file_creator.domain.models.file_creation_model import FileCreationItem

class IFileCreatorRepository(ABC):
    @abstractmethod
    def read_creation_data(self, json_path: str) -> List[FileCreationItem]:
        pass

    @abstractmethod
    def write_files(self, base_dir: str, files: List[FileCreationItem]) -> List[str]:
        pass