from pathlib import Path
import os
from typing import Callable, Optional, List

from src.features.project_mapper.domain.models.mapping_config_model import MappingConfig
from src.features.project_mapper.domain.models.directory_node_model import DirectoryNode
from src.features.project_mapper.domain.repositories.i_project_mapper_repository import IProjectMapperRepository

class FilesystemProjectMapperRepository(IProjectMapperRepository):
    EXCLUDED_DIRS = {'.git', '.idea', 'venv', '__pycache__', 'node_modules', '.vscode', 'build', 'dist', '.pytest_cache'}

    def get_directory_tree(self, path: str) -> Optional[DirectoryNode]:
        root_path = Path(path)
        if not root_path.is_dir():
            return None

        def build_tree(current_path: Path, relative_root: Path, parent: Optional[DirectoryNode] = None) -> DirectoryNode:
            node_path_str = current_path.relative_to(relative_root).as_posix()
            if node_path_str == '.': node_path_str = ''

            node = DirectoryNode(
                name=current_path.name if node_path_str else relative_root.name,
                path=node_path_str,
                parent=parent
            )
            
            try:
                children = sorted(current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
                for item in children:
                    if item.is_dir() and item.name not in self.EXCLUDED_DIRS:
                        node.children.append(build_tree(item, relative_root, parent=node))
            except OSError:
                pass
            return node

        return build_tree(root_path, root_path)

    def _get_files_to_process(self, config: MappingConfig) -> List[Path]:
        project_path = Path(config.project_dir)
        selected_dirs = config.selected_dirs
        is_full_scan = not selected_dirs

        all_files = set()

        for root, dirs, files in os.walk(project_path, topdown=True):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS]

            if is_full_scan:
                for filename in files:
                    all_files.add(Path(root) / filename)
                continue

            current_path_str = Path(root).relative_to(project_path).as_posix()
            if current_path_str == '.':
                current_path_str = ''

            should_add_files = any(
                current_path_str == sel_dir or current_path_str.startswith(sel_dir + '/')
                for sel_dir in selected_dirs
            )
            if should_add_files:
                for filename in files:
                    all_files.add(Path(root) / filename)

            is_potential_ancestor = any(
                sel_dir.startswith(current_path_str)
                for sel_dir in selected_dirs
            )
            if not is_potential_ancestor:
                dirs.clear()

        return sorted(list(all_files))

    def _generate_map_content_stream(self, config: MappingConfig, files_to_process: List[Path]):
        project_path = Path(config.project_dir)
        include_set = {ext.lower() for ext in config.include_extensions}
        exclude_set = {pat.lower() for pat in config.exclude_patterns}
        found_files = 0

        yield f"# Mapeo del Proyecto: {project_path.name}\n\n"
        yield f"Directorio base: `{config.project_dir}`\n"
        yield f"Extensiones incluidas: `{', '.join(config.include_extensions) if config.include_extensions else 'Todas (excepto excluidas)'}`\n"
        yield f"Patrones excluidos: `{', '.join(config.exclude_patterns) if config.exclude_patterns else 'Ninguno'}`\n\n---\n\n"

        for item_path in files_to_process:
            file_ext_lower = item_path.suffix.lower()
            file_name_lower = item_path.name.lower()
            included = not include_set or file_ext_lower in include_set
            excluded = any(file_name_lower.endswith(p) for p in exclude_set)

            if included and not excluded:
                found_files += 1
                relative_path = item_path.relative_to(project_path).as_posix()
                yield f"## `{relative_path}`\n\n"
                lang_hint = file_ext_lower.lstrip('.')
                yield f"```{lang_hint}\n"
                try:
                    with open(item_path, "r", encoding="utf-8", errors='ignore') as in_f:
                        yield in_f.read()
                except Exception as e:
                    yield f"Error al leer el archivo: {e}"
                yield "\n```\n\n"

    def map_project(
        self, 
        config: MappingConfig, 
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> int:
        project_path = Path(config.project_dir)
        if not project_path.is_dir():
            raise NotADirectoryError(f"La ruta del proyecto no es un directorio: {config.project_dir}")

        files_to_process = self._get_files_to_process(config)
        if progress_callback:
            progress_callback(f"Recorriendo {len(files_to_process)} archivos...")

        with open(config.output_file, "w", encoding="utf-8") as out_f:
            for content_part in self._generate_map_content_stream(config, files_to_process):
                out_f.write(content_part)
        
        return len(files_to_process)