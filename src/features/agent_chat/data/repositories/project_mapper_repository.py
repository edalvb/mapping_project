import os
from io import StringIO
from pathlib import Path
from typing import List, Set

from ...domain.repositories.i_project_mapper_repository import (
    IProjectMapperRepository,
)


class ProjectMapperRepository(IProjectMapperRepository):
    def map_project_to_string(
        self,
        project_dir: str,
        extensions_to_include: List[str],
        extensions_to_exclude: List[str],
    ) -> str:
        project_path = Path(project_dir)
        if not project_path.is_dir():
            raise FileNotFoundError(f"Project directory not found: {project_dir}")

        output_buffer = StringIO()
        self._write_header(
            output_buffer,
            project_path.name,
            project_dir,
            extensions_to_include,
            extensions_to_exclude,
        )

        include_set = self._prepare_extension_set(extensions_to_include)
        exclude_set = self._prepare_extension_set(extensions_to_exclude)

        for root, _, files in os.walk(project_dir):
            current_dir_path = Path(root)
            for filename in files:
                file_path = current_dir_path / filename
                if self._should_include_file(file_path, include_set, exclude_set):
                    self._append_file_content(output_buffer, file_path, project_path)

        return output_buffer.getvalue()

    def _write_header(
        self,
        buffer: StringIO,
        project_name: str,
        project_dir: str,
        include_list: List[str],
        exclude_list: List[str],
    ) -> None:
        buffer.write(f"# Mapeo del Proyecto: {project_name}\n\n")
        buffer.write(f"Directorio base: `{project_dir}`\n")
        include_str = ", ".join(include_list) if include_list else "Todas"
        exclude_str = ", ".join(exclude_list) if exclude_list else "Ninguna"
        buffer.write(f"Extensiones incluidas: `{include_str}`\n")
        buffer.write(f"Extensiones excluidas: `{exclude_str}`\n\n")
        buffer.write("---\n\n")

    def _prepare_extension_set(self, extensions: List[str]) -> Set[str]:
        return {ext.lower() for ext in extensions if ext.startswith(".")}

    def _should_include_file(
        self, file_path: Path, include_set: Set[str], exclude_set: Set[str]
    ) -> bool:
        file_ext_lower = file_path.suffix.lower()

        if file_ext_lower in exclude_set:
            return False

        if not include_set:
            return True

        return file_ext_lower in include_set

    def _append_file_content(
        self, buffer: StringIO, file_path: Path, project_path: Path
    ) -> None:
        relative_path = file_path.relative_to(project_path)
        lang_hint = file_path.suffix.lstrip(".")

        buffer.write(f"## `{relative_path}`\n\n")
        buffer.write(f"```{lang_hint}\n")

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            content = "Error: No se pudo leer el contenido del archivo."

        buffer.write(content)
        buffer.write("\n```\n\n")
