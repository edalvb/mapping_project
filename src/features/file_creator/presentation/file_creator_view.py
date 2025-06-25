import flet as ft
from  src.features.file_creator.presentation.file_creator_controller import FileCreatorController
from src.features.file_creator.presentation.file_creator_state import FileCreatorState
from src.shared.presentation.theme import CORTEX_AI_PALETTE

class FileCreatorView(ft.Container):
    def __init__(self, controller: FileCreatorController, state: FileCreatorState):
        super().__init__()
        self.controller = controller
        self.state = state
        
        self.padding = ft.padding.all(20)
        self.content = ft.Column(
            [
                ft.Text("Crear Estructura desde JSON", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Row([
                    ft.ElevatedButton("Seleccionar Ruta Base", icon=ft.Icons.FOLDER_OPEN, on_click=self.controller.pick_base_dir),
                    ft.Text(self.state.base_dir_path or "Ruta no seleccionada", expand=True, no_wrap=True),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Row([
                    ft.ElevatedButton("Seleccionar Archivo JSON", icon=ft.Icons.UPLOAD_FILE, on_click=self.controller.pick_json_file),
                    ft.Text(self.state.json_file_path or "JSON no seleccionado", expand=True, no_wrap=True),
                 ], alignment=ft.MainAxisAlignment.START),
                ft.Divider(height=20),
                ft.ElevatedButton(
                    "Crear Archivos",
                    icon=ft.Icons.CREATE_NEW_FOLDER,
                    on_click=self.controller.start_creation_process,
                    bgcolor=CORTEX_AI_PALETTE.secondary,
                    color=CORTEX_AI_PALETTE.on_secondary,
                    disabled=self.state.is_loading,
                ),
                ft.Row([
                    ft.ProgressRing(width=16, height=16, stroke_width=2, visible=self.state.is_loading),
                    ft.Text(self.state.status_text, expand=True, selectable=True)
                ], visible=True),
            ], 
            spacing=15, 
            scroll=ft.ScrollMode.ADAPTIVE,
        )