import flet as ft
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Set

from src.features.project_mapper.domain.models.mapping_config_model import MappingConfig
from src.features.project_mapper.domain.services.project_mapper_service import ProjectMapperService
from src.features.project_mapper.presentation.project_mapper_state import ProjectMapperState
from src.shared.presentation.dialogs import show_dialog, show_snackbar

if TYPE_CHECKING:
    from src.features.project_mapper.presentation.project_mapper_view import ProjectMapperView

class ProjectMapperController:
    def __init__(self, page: ft.Page, state: ProjectMapperState, service: ProjectMapperService):
        self.page = page
        self.state = state
        self.service = service
        self.view: 'ProjectMapperView' = None

        self._project_dir_picker = ft.FilePicker(on_result=self._on_project_dir_result)
        self._output_dir_picker = ft.FilePicker(on_result=self._on_output_dir_result)
        self.page.overlay.extend([self._project_dir_picker, self._output_dir_picker])

    def _load_subdirectories(self, path: str):
        try:
            dirs = self.service.get_subdirectories(path)
            self.state.subdirectories = {d: True for d in dirs}
        except Exception as e:
            self.state.subdirectories = {}
            show_dialog(self.page, "Error al leer subdirectorios", str(e))

    def _on_project_dir_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.state.project_dir_path = e.path
            project_folder_name = Path(e.path).name
            self.state.output_filename = f"{project_folder_name}.md"
            if not self.state.output_dir_path:
                self.state.output_dir_path = str(Path.cwd())
            self._load_subdirectories(e.path)
        if self.view:
            self.view.update_view()

    def _on_output_dir_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.state.output_dir_path = e.path
        if self.view:
            self.view.update_view()

    def pick_project_dir(self, e):
        self._project_dir_picker.get_directory_path(dialog_title="Seleccionar carpeta del proyecto")

    def pick_output_dir(self, e):
        self._output_dir_picker.get_directory_path(dialog_title="Seleccionar carpeta de salida")

    def on_toggle_directory(self, e):
        dir_name = e.control.data
        if dir_name in self.state.subdirectories:
            self.state.subdirectories[dir_name] = e.control.value
        if self.view:
            self.view.update_view()

    def on_change_output_filename(self, e):
        self.state.output_filename = e.control.value

    def on_change_include_text(self, e):
        self.state.new_include_extension = e.control.value

    def on_change_exclude_text(self, e):
        self.state.new_exclude_pattern = e.control.value

    def add_include_extension(self, e):
        ext = self.state.new_include_extension.strip().lower()
        if not ext: return
        if not ext.startswith("."): ext = "." + ext
        if ext not in self.state.include_extensions:
            self.state.include_extensions.add(ext)
            self.state.new_include_extension = ""
        else:
            show_snackbar(self.page, f"La inclusión '{ext}' ya existe.", is_error=True)
        if self.view: self.view.update_view()

    def delete_include_extension(self, e):
        ext_to_delete = e.control.data
        self.state.include_extensions.discard(ext_to_delete)
        if self.view: self.view.update_view()

    def add_exclude_pattern(self, e):
        pat = self.state.new_exclude_pattern.strip().lower()
        if not pat: return
        if pat not in self.state.exclude_patterns:
            self.state.exclude_patterns.add(pat)
            self.state.new_exclude_pattern = ""
        else:
            show_snackbar(self.page, f"La exclusión '{pat}' ya existe.", is_error=True)
        if self.view: self.view.update_view()

    def delete_exclude_pattern(self, e):
        pat_to_delete = e.control.data
        self.state.exclude_patterns.discard(pat_to_delete)
        if self.view: self.view.update_view()

    def start_mapping_process(self, e):
        if not self.state.project_dir_path:
            show_dialog(self.page, "Error", "Debe seleccionar una carpeta de proyecto.")
            return
        if not self.state.output_dir_path or not self.state.output_filename:
            show_dialog(self.page, "Error", "Debe especificar una carpeta y un nombre de archivo de salida.")
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
        selected_dirs: Set[str] = {d for d, checked in self.state.subdirectories.items() if checked}

        config = MappingConfig(
            project_dir=self.state.project_dir_path,
            selected_dirs=selected_dirs,
            include_extensions=self.state.include_extensions,
            exclude_patterns=self.state.exclude_patterns,
            output_file=str(output_path)
        )

        try:
            found_files = self.service.execute(config, self._update_progress)
            final_message = f"¡Éxito! Mapeo completado. {found_files} archivos incluidos en '{self.state.output_filename}'."
            self.state.status_text = final_message
            show_snackbar(self.page, f"Archivo Markdown generado: {self.state.output_filename}")
        except Exception as e:
            self.state.status_text = f"Error durante el mapeo: {e}"
            show_dialog(self.page, "Error de Mapeo", f"Ocurrió un error: {e}")
        finally:
            self.state.is_loading = False
            if self.view: self.view.update_view()
