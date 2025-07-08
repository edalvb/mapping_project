from pathlib import Path
import os
from typing import Callable, Optional

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

            node = DirectoryNode(
                name=current_path.name,
                path=node_path_str,
                parent=parent
            )
            if node.path == '.':
                node.path = ''
                node.name = relative_root.name

            try:
                children = sorted(current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
                for item in children:
                    if item.is_dir() and item.name not in self.EXCLUDED_DIRS:
                        node.children.append(build_tree(item, relative_root, parent=node))
            except OSError:
                pass
            return node

        return build_tree(root_path, root_path)

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
        
        selected_relative_dirs = config.selected_dirs

        with open(output_path, "w", encoding="utf-8") as out_f:
            out_f.write(f"# Mapeo del Proyecto: {project_path.name}\n\n")
            out_f.write(f"Directorio base: `{config.project_dir}`\n")
            out_f.write(f"Extensiones incluidas: `{', '.join(config.include_extensions) if config.include_extensions else 'Todas (excepto excluidas)'}`\n")
            out_f.write(f"Patrones excluidos: `{', '.join(config.exclude_patterns) if config.exclude_patterns else 'Ninguno'}`\n\n")
            out_f.write("---\n\n")

            if progress_callback:
                progress_callback("Recorriendo directorios...")

            all_files_to_process = set()
            
            for root, dirs, files in os.walk(project_path, topdown=True):
                dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS]
                
                current_path = Path(root)
                relative_current_path_str = current_path.relative_to(project_path).as_posix()

                if relative_current_path_str == '.':
                    relative_current_path_str = ''

                if relative_current_path_str not in selected_relative_dirs:
                    dirs[:] = []
                    continue

                for filename in files:
                    all_files_to_process.add(current_path / filename)

            for item_path in sorted(list(all_files_to_process)):
                file_ext_lower = item_path.suffix.lower()
                file_name_lower = item_path.name.lower()

                included = not include_extensions_set or file_ext_lower in include_extensions_set
                excluded = any(file_name_lower.endswith(p) for p in exclude_patterns_set)

                if included and not excluded:
                    found_files += 1
                    relative_path = item_path.relative_to(project_path).as_posix()
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
