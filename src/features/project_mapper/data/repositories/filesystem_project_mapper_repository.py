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
                is_directory=True,
                parent=parent
            )
            
            try:
                # Separar archivos y directorios
                items = list(current_path.iterdir())
                directories = [item for item in items if item.is_dir() and item.name not in self.EXCLUDED_DIRS]
                files = [item for item in items if item.is_file()]
                
                # Ordenar: primero directorios, luego archivos, ambos alfabéticamente
                all_items = sorted(directories, key=lambda p: p.name.lower()) + sorted(files, key=lambda p: p.name.lower())
                
                for item in all_items:
                    if item.is_dir():
                        # Agregar directorio
                        child_node = build_tree(item, relative_root, parent=node)
                        node.children.append(child_node)
                    else:
                        # Agregar archivo
                        file_path_str = item.relative_to(relative_root).as_posix()
                        file_node = DirectoryNode(
                            name=item.name,
                            path=file_path_str,
                            is_directory=False,
                            parent=node
                        )
                        node.children.append(file_node)
                        
            except OSError:
                pass
            return node

        return build_tree(root_path, root_path)

    def _get_files_to_process(self, config: MappingConfig) -> List[Path]:
        project_path = Path(config.project_dir)
        selected_paths = config.selected_paths
        
        # Si no hay selecciones, no procesar nada
        # El usuario debe seleccionar explícitamente qué quiere incluir
        if not selected_paths:
            return []

        all_files = set()

        # Separar archivos individuales de directorios seleccionados
        selected_files = set()
        selected_directories = set()
        
        for path in selected_paths:
            # Limpiar paths vacíos que pueden causar problemas
            if path == "":
                # Path vacío representa el directorio raíz
                selected_directories.add("")
                continue
                
            full_path = project_path / path
            if full_path.is_file():
                selected_files.add(path)
            elif full_path.is_dir():
                selected_directories.add(path)

        # Agregar archivos individuales seleccionados
        for file_path_str in selected_files:
            file_path = project_path / file_path_str
            if file_path.exists() and file_path.is_file():
                all_files.add(file_path)

        # Si se seleccionó el directorio raíz (path vacío), incluir todo
        if "" in selected_directories:
            for root, dirs, files in os.walk(project_path, topdown=True):
                dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS]
                for filename in files:
                    all_files.add(Path(root) / filename)
            return sorted(list(all_files))

        # Procesar directorios seleccionados (excluyendo el raíz)
        selected_directories.discard("")  # Remover path vacío si existe
        
        for root, dirs, files in os.walk(project_path, topdown=True):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS]
            
            current_path_str = Path(root).relative_to(project_path).as_posix()
            if current_path_str == '.':
                current_path_str = ''

            # Verificar si el directorio actual está seleccionado
            is_directory_selected = any(
                current_path_str == sel_dir or 
                (sel_dir and current_path_str.startswith(sel_dir + '/'))
                for sel_dir in selected_directories
            )

            if is_directory_selected:
                # Si el directorio está seleccionado, verificar cada archivo individualmente
                for filename in files:
                    file_path = Path(root) / filename
                    file_path_str = file_path.relative_to(project_path).as_posix()
                    
                    # LÓGICA FINAL CORRECTA:
                    # En el controlador:
                    # - Seleccionar directorio → agrega directorio + todos sus archivos a selected_paths
                    # - Deseleccionar archivo específico → quita solo ese archivo de selected_paths
                    # 
                    # Por tanto aquí solo necesitamos verificar:
                    # ¿Está este archivo específico en selected_paths?
                    
                    if file_path_str in selected_paths:
                        all_files.add(file_path)
            
            # Verificar si necesitamos continuar explorando subdirectorios
            should_continue = any(
                sel_dir.startswith(current_path_str + '/') if current_path_str else sel_dir
                for sel_dir in selected_directories
                if sel_dir  # Ignorar paths vacíos
            )
            
            if not should_continue:
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