from pathlib import Path
import os
from typing import Set, Callable, Optional, List

from src.features.project_mapper.domain.models.mapping_config_model import MappingConfig
from src.features.project_mapper.domain.repositories.i_project_mapper_repository import IProjectMapperRepository

class FilesystemProjectMapperRepository(IProjectMapperRepository):
    def get_subdirectories(self, path: str) -> List[str]:
        root_path = Path(path)
        if not root_path.is_dir():
            return []
        return sorted([d.name for d in root_path.iterdir() if d.is_dir()])

    def map_project(
        self, 
        config: MappingConfig, 
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> int:
        project_path = Path(config.project_dir)
        output_path = Path(config.output_file)

        if not project_path.is_dir():
            raise NotADirectoryError(f"La ruta del proyecto no es un directorio: {config.project_dir}")

        include_extensions_set = {ext.lower() for ext in config.include_extensions}
        exclude_patterns_set = {pat.lower() for pat in config.exclude_patterns}
        found_files = 0

        with open(output_path, "w", encoding="utf-8") as out_f:
            out_f.write(f"# Mapeo del Proyecto: {project_path.name}\n\n")
            out_f.write(f"Directorio base: `{config.project_dir}`\n")
            out_f.write(f"Extensiones incluidas: `{', '.join(config.include_extensions) if config.include_extensions else 'Todas (excepto excluidas)'}`\n")
            out_f.write(f"Patrones excluidos: `{', '.join(config.exclude_patterns) if config.exclude_patterns else 'Ninguno'}`\n\n")
            out_f.write("---\n\n")

            if progress_callback:
                progress_callback("Recorriendo directorios...")
            
            dirs_to_walk = [project_path.joinpath(d) for d in config.selected_dirs]
            if not dirs_to_walk:
                dirs_to_walk = [project_path]

            for dir_path in dirs_to_walk:
                for root, _, files in os.walk(dir_path):
                    current_dir_path = Path(root)
                    for filename in files:
                        item_path = current_dir_path / filename
                        file_ext_lower = item_path.suffix.lower()
                        file_name_lower = item_path.name.lower()

                        included = not include_extensions_set or file_ext_lower in include_extensions_set
                        excluded = any(file_name_lower.endswith(p) for p in exclude_patterns_set)

                        if included and not excluded:
                            found_files += 1
                            relative_path = item_path.relative_to(project_path)
                            if progress_callback:
                                progress_callback(f"Mapeando ({found_files}): {relative_path}")
                            
                            out_f.write(f"## `{relative_path}`\n\n")
                            lang_hint = file_ext_lower.lstrip('.')
                            out_f.write(f"```{lang_hint}\n")
                            try:
                                with open(item_path, "r", encoding="utf-8", errors='ignore') as in_f:
                                    content = in_f.read()
                            except Exception as e:
                                content = f"Error al leer el archivo: {e}"
                            out_f.write(content)
                            out_f.write("\n```\n\n")
        return found_files
