import flet as ft
import threading

from src.features.file_creator.domain.services.file_creator_service import FileCreatorService
from src.features.file_creator.presentation.file_creator_state import FileCreatorState
from src.shared.presentation.dialogs import show_dialog, show_snackbar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.features.file_creator.presentation.file_creator_view import FileCreatorView

class FileCreatorController:
    def __init__(self, page: ft.Page, state: FileCreatorState, service: FileCreatorService):
        self.page = page
        self.state = state
        self.service = service
        self.view: 'FileCreatorView' = None

        self._base_dir_picker = ft.FilePicker(on_result=self._on_base_dir_result)
        self._json_file_picker = ft.FilePicker(on_result=self._on_json_file_result)
        self.page.overlay.extend([self._base_dir_picker, self._json_file_picker])

    def _on_base_dir_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.state.base_dir_path = e.path
        if self.view:
            self.view.update_view()

    def _on_json_file_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.state.json_file_path = e.files[0].path
        if self.view:
            self.view.update_view()

    def pick_base_dir(self, e):
        self._base_dir_picker.get_directory_path(dialog_title="Seleccionar directorio base")

    def pick_json_file(self, e):
        self._json_file_picker.pick_files(
            dialog_title="Seleccionar archivo JSON",
            allow_multiple=False,
            allowed_extensions=["json"]
        )

    def start_creation_process(self, e):
        if not self.state.base_dir_path:
            show_dialog(self.page, "Error", "Debe seleccionar una ruta base.")
            return
        if not self.state.json_file_path:
            show_dialog(self.page, "Error", "Debe seleccionar un archivo JSON.")
            return

        thread = threading.Thread(target=self._creation_thread_worker)
        thread.start()
    
    def _creation_thread_worker(self):
        self.state.is_loading = True
        self.state.status_text = "Iniciando..."
        if self.view: self.view.update_view()

        try:
            total_items, errors = self.service.execute(self.state.base_dir_path, self.state.json_file_path)
            processed_count = total_items - len(errors)

            if not errors:
                self.state.status_text = f"¡Éxito! {processed_count} archivos creados correctamente."
                show_snackbar(self.page, "¡Archivos creados correctamente!")
            else:
                self.state.status_text = f"Completado con {len(errors)} errores. {processed_count} archivos creados."
                error_details = "\n".join(errors[:10])
                if len(errors) > 10:
                    error_details += f"\n... ({len(errors) - 10} errores más)"
                show_dialog(self.page, "Proceso completado con errores", error_details)
        
        except Exception as e:
            self.state.status_text = f"Error crítico: {e}"
            show_dialog(self.page, "Error Crítico", f"Ocurrió un error inesperado: {e}")
        finally:
            self.state.is_loading = False
            if self.view: self.view.update_view()
