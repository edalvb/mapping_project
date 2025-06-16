from abc import ABC, abstractmethod

class IFileSystemRepository(ABC):

    @abstractmethod
    def write_file(self, file_path: str, content: str) -> None:
        pass

    @abstractmethod
    def is_directory(self, path: str) -> bool:
        pass
