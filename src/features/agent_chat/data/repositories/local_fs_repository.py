from pathlib import Path

from ...domain.repositories.i_file_system_repository import IFileSystemRepository


class LocalFsRepository(IFileSystemRepository):

    def write_file(self, file_path: str, content: str) -> None:
        try:
            full_path = Path(file_path).resolve()
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as e:
            raise IOError(f"Failed to write file at {file_path}: {e}") from e

    def is_directory(self, path: str) -> bool:
        return Path(path).is_dir()
