import flet as ft
import threading
import tempfile
import os
from pathlib import Path
from typing import TYPE_CHECKING, Set, Optional

from src.features.project_mapper.domain.models.mapping_config_model import MappingConfig
from src.features.project_mapper.domain.models.directory_node_model import DirectoryNode
from src.features.project_mapper.domain.models.llm_config_model import LLMConfig
from src.features.project_mapper.domain.services.project_mapper_service import ProjectMapperService
from src.features.project_mapper.presentation.project_mapper_state import ProjectMapperState
from src.shared.presentation.dialogs import show_dialog, show_snackbar

if TYPE_CHECKING:
    from src.features.project_mapper.presentation.view.project_mapper_view import ProjectMapperView

class ProjectMapperController:
    def __init__(self, page: ft.Page, state: ProjectMapperState, service: ProjectMapperService):
        self.page = page
        self.state = state
        self.service = service
        self.view: 'ProjectMapperView' = None

        self._project_dir_picker = ft.FilePicker(on_result=self._on_project_dir_result)
        self._output_dir_picker = ft.FilePicker(on_result=self._on_output_dir_result)
        self.page.overlay.extend([self._project_dir_picker, self._output_dir_picker])
        
        self.state.llm_api_key = os.environ.get("GEMINI_API_KEY", "")

    def on_view_did_mount(self):
        if self.state.llm_api_key:
            thread = threading.Thread(target=self._load_models_worker)
            thread.start()

    def _load_models_worker(self):
        self.state.is_ai_selecting = True
        self.state.ai_status_text = "Verificando clave y cargando modelos..."
        if self.view: self.view.update_view()

        try:
            models = self.service.get_available_llm_models(api_key=self.state.llm_api_key)

            self.state.available_llm_models = models
            self.state.llm_models_loaded = True
            if models and not self.state.selected_llm_model:
                self.state.selected_llm_model = models[0]
            self.state.ai_status_text = f"{len(models)} modelos cargados con éxito."
        except Exception as e:
            self.state.available_llm_models = []
            self.state.llm_models_loaded = False
            self.state.ai_status_text = f"Error al cargar modelos: {e}"
        finally:
            self.state.is_ai_selecting = False
            if self.view: self.view.update_view()

    def _load_directory_tree(self, path: str):
        try:
            tree = self.service.get_directory_tree(path)
            self.state.directory_tree = tree
            self.state.selected_dirs.clear()
            if tree:
                self.state.selected_dirs.add(tree.path)
        except Exception as e:
            self.state.directory_tree = None
            show_dialog(self.page, "Error al leer directorios", str(e))

    def _on_project_dir_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.state.project_dir_path = e.path
            project_folder_name = Path(e.path).name
            self.state.output_filename = f"{project_folder_name}_map.md"
            if not self.state.output_dir_path:
                self.state.output_dir_path = str(Path.cwd())
            self._load_directory_tree(e.path)
        if self.view: self.view.update_view()

    def _on_output_dir_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.state.output_dir_path = e.path
        if self.view: self.view.update_view()

    def pick_project_dir(self, e): self._project_dir_picker.get_directory_path(dialog_title="Seleccionar carpeta del proyecto")
    def pick_output_dir(self, e): self._output_dir_picker.get_directory_path(dialog_title="Seleccionar carpeta de salida")
    def on_change_output_filename(self, e): self.state.output_filename = e.control.value
    def on_change_include_text(self, e): self.state.new_include_extension = e.control.value
    def on_change_exclude_text(self, e): self.state.new_exclude_pattern = e.control.value
    def on_change_llm_system_instruction(self, e): self.state.llm_system_instruction = e.control.value
    def on_change_llm_objective(self, e): self.state.llm_objective = e.control.value
    def on_change_selected_model(self, e): self.state.selected_llm_model = e.control.value
    
    def on_change_llm_api_key(self, e):
        self.state.llm_api_key = e.control.value
        self.state.llm_models_loaded = False
        self.state.available_llm_models = []
        self.state.selected_llm_model = None
        if self.view: self.view.update_view()

    def verify_and_load_models(self, e):
        if not self.state.llm_api_key:
            show_dialog(self.page, "Error", "Debe introducir una clave de API.")
            return
        thread = threading.Thread(target=self._load_models_worker)
        thread.start()

    def on_directory_toggle(self, e: ft.ControlEvent):
        node: Optional[DirectoryNode] = e.control.data.app_data if hasattr(e.control.data, 'app_data') else None
        if not node: return

        is_selected = e.control.value
        paths_to_change: Set[str] = set()
        q = [node]
        while q: 
            curr = q.pop(0)
            paths_to_change.add(curr.path)
            q.extend(curr.children)
        
        if is_selected: self.state.selected_dirs.update(paths_to_change)
        else: self.state.selected_dirs.difference_update(paths_to_change)
        
        if self.view: self.view.update_view()

    def add_include_extension(self, e):
        ext = self.state.new_include_extension.strip().lower()
        if not ext: return
        if not ext.startswith("."): ext = "." + ext
        self.state.include_extensions.add(ext)
        self.state.new_include_extension = ""
        if self.view: self.view.update_view()

    def delete_include_extension(self, e):
        self.state.include_extensions.discard(e.control.data)
        if self.view: self.view.update_view()

    def add_exclude_pattern(self, e):
        pat = self.state.new_exclude_pattern.strip().lower()
        if not pat: return
        self.state.exclude_patterns.add(pat)
        self.state.new_exclude_pattern = ""
        if self.view: self.view.update_view()

    def delete_exclude_pattern(self, e):
        self.state.exclude_patterns.discard(e.control.data)
        if self.view: self.view.update_view()

    def start_mapping_process(self, e):
        if not self.state.project_dir_path or not self.state.output_dir_path or not self.state.output_filename:
            show_dialog(self.page, "Error", "Debe especificar un proyecto, carpeta y nombre de archivo de salida.")
            return
        thread = threading.Thread(target=self._mapping_thread_worker)
        thread.start()

    def _update_progress(self, message: str):
        self.state.status_text = message
        if self.view: self.view.update_view()

    def _mapping_thread_worker(self):
        self.state.is_loading = True
        self.state.status_text = "Iniciando mapeo..."
        if self.view: self.view.update_view()

        output_path = Path(self.state.output_dir_path) / self.state.output_filename
        config = MappingConfig(project_dir=self.state.project_dir_path, selected_dirs=self.state.selected_dirs, include_extensions=self.state.include_extensions, exclude_patterns=self.state.exclude_patterns, output_file=str(output_path))

        try:
            found_files = self.service.execute_mapping_to_file(config, self._update_progress)
            self.state.status_text = f"¡Éxito! Mapeo completado. {found_files} archivos procesados."
            show_snackbar(self.page, f"Archivo generado: {self.state.output_filename}")
        except Exception as e:
            self.state.status_text = f"Error durante el mapeo: {e}"
            show_dialog(self.page, "Error de Mapeo", str(e))
        finally:
            self.state.is_loading = False
            if self.view: self.view.update_view()

    def start_intelligent_selection(self, e):
        if not self.state.project_dir_path: show_dialog(self.page, "Error", "Seleccione un proyecto primero."); return
        if not self.state.llm_models_loaded: show_dialog(self.page, "Error", "Verifique su clave API y cargue los modelos primero."); return
        if not self.state.llm_objective.strip(): show_dialog(self.page, "Error", "Defina un objetivo para la IA."); return
        if not self.state.selected_llm_model: show_dialog(self.page, "Error", "Seleccione un modelo de IA."); return

        thread = threading.Thread(target=self._intelligent_selection_worker)
        thread.start()

    def _intelligent_selection_worker(self):
        self.state.is_ai_selecting = True
        self.state.ai_status_text = "Generando mapa de contexto para la IA..."
        if self.view: self.view.update_view()

        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".md", encoding='utf-8') as tf:
                temp_file = tf.name
            
            map_config = MappingConfig(project_dir=self.state.project_dir_path, selected_dirs=set(), include_extensions=set(), exclude_patterns=set(), output_file=temp_file)
            self.service.execute_mapping_to_file(map_config, self._update_ai_status)
            
            with open(temp_file, 'r', encoding='utf-8') as f:
                map_content = f.read()

            self.state.ai_status_text = "Contexto enviado a la IA. Esperando selección..."
            if self.view: self.view.update_view()

            llm_config = LLMConfig(system_instruction=self.state.llm_system_instruction, objective=self.state.llm_objective, model_name=self.state.selected_llm_model, api_key=self.state.llm_api_key)
            suggested_paths = self.service.get_intelligent_folder_selection(llm_config, map_content)
            self.state.selected_dirs = suggested_paths

            show_snackbar(self.page, "Selección de carpetas por IA completada.")
            self.state.ai_status_text = ""

        except Exception as e:
            show_dialog(self.page, "Error en Selección Inteligente", str(e))
            self.state.ai_status_text = f"Error: {e}"
        finally:
            self.state.is_ai_selecting = False
            if temp_file and os.path.exists(temp_file): os.remove(temp_file)
            if self.view: self.view.update_view()

    def _update_ai_status(self, message: str):
        self.state.ai_status_text = message
        if self.view: self.view.update_view()

    def on_tab_change(self, e: ft.ControlEvent):
        self.state.right_panel_tab_index = e.control.selected_index