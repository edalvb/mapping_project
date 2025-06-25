from typing import List, Tuple
from src.features.file_creator.domain.repositories.i_file_creator_repository import IFileCreatorRepository

class FileCreatorService:
    def __init__(self, repository: IFileCreatorRepository):
        self._repository = repository

    def execute(self, base_dir: str, json_path: str) -> Tuple[int, List[str]]:
        files_to_create = self._repository.read_creation_data(json_path)
        total_items = len(files_to_create)
        errors = self._repository.write_files(base_dir, files_to_create)
        return total_items, errors