from pathlib import Path
import json
from typing import List, Dict, Any

from src.features.file_creator.domain.models.file_creation_model import FileCreationItem
from src.features.file_creator.domain.repositories.i_file_creator_repository import IFileCreatorRepository

class FilesystemFileCreatorRepository(IFileCreatorRepository):
    def read_creation_data(self, json_path: str) -> List[FileCreationItem]:
        json_file_path = Path(json_path)
        if not json_file_path.is_file():
            raise FileNotFoundError(f"El archivo JSON no se encontró en: {json_path}")

        with open(json_file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error al decodificar el archivo JSON: {e}")

        if not isinstance(data, list):
            raise TypeError("El contenido del JSON debe ser una lista de objetos.")

        items = []
        for item_data in data:
            if not isinstance(item_data, dict) or "path" not in item_data or "content" not in item_data:
                raise ValueError("Un objeto en el JSON no tiene 'path' o 'content'.")
            items.append(FileCreationItem(**item_data))
        return items

    def write_files(self, base_dir: str, files: List[FileCreationItem]) -> List[str]:
        base_dir_path = Path(base_dir)
        if not base_dir_path.is_dir():
            raise NotADirectoryError(f"La ruta base no es un directorio válido: {base_dir}")

        errors: List[str] = []
        base_dir_resolved = base_dir_path.resolve()

        for item in files:
            try:
                full_path = base_dir_path.joinpath(item.path).resolve()

                if base_dir_resolved not in full_path.parents and full_path != base_dir_resolved:
                    errors.append(f"Intento de escritura fuera del directorio base: '{item.path}'. Omitido.")
                    continue

                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(item.content)
            except OSError as e:
                errors.append(f"Error de OS al procesar '{item.path}': {e}")
            except Exception as e:
                errors.append(f"Error inesperado al procesar '{item.path}': {e}")
        
        return errors