import flet as ft
from src.features.project_mapper.presentation.project_mapper_controller import ProjectMapperController
from src.features.project_mapper.presentation.project_mapper_state import ProjectMapperState
from src.features.project_mapper.presentation.widgets.extensions_list_widget import ExtensionsListWidget
from src.shared.presentation.theme import CORTEX_AI_PALETTE

class ProjectMapperView(ft.Container):
    def __init__(self, controller: ProjectMapperController, state: ProjectMapperState):
        super().__init__()
        self.controller = controller
        self.state = state

        self.padding = ft.padding.all(20)
        self.content = ft.Column(
            [
                ft.Text("Mapear Proyecto a Markdown", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Row([
                    ft.ElevatedButton("Seleccionar Carpeta Proyecto", icon=ft.Icons.FOLDER_OPEN, on_click=self.controller.pick_project_dir),
                    ft.Text(self.state.project_dir_path or "Ruta no seleccionada", expand=True, no_wrap=True),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Divider(height=10),
                ft.Row(
                    [
                        ExtensionsListWidget(
                            title="Extensiones a incluir (ej: .py)",
                            items=sorted(list(self.state.include_extensions)),
                            new_item_value=self.state.new_include_extension,
                            on_add=self.controller.add_include_extension,
                            on_delete=self.controller.delete_include_extension,
                            on_change_new_item=self.controller.on_change_include_text,
                            on_submit_new_item=self.controller.add_include_extension
                        ),
                        ExtensionsListWidget(
                            title="Patrones a excluir (ej: .g.dart)",
                            items=sorted(list(self.state.exclude_patterns)),
                            new_item_value=self.state.new_exclude_pattern,
                            on_add=self.controller.add_exclude_pattern,
                            on_delete=self.controller.delete_exclude_pattern,
                            on_change_new_item=self.controller.on_change_exclude_text,
                            on_submit_new_item=self.controller.add_exclude_pattern
                        ),
                    ],
                    spacing=15,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    height=280
                ),
                ft.Divider(height=20),
                ft.ElevatedButton(
                    "Iniciar Mapeo",
                    icon=ft.Icons.DOCUMENT_SCANNER,
                    on_click=self.controller.start_mapping_process,
                    bgcolor=CORTEX_AI_PALETTE.primary,
                    color=CORTEX_AI_PALETTE.on_primary,
                    disabled=self.state.is_loading,
                ),
                ft.Row([
                    ft.ProgressRing(width=16, height=16, stroke_width=2, visible=self.state.is_loading),
                    ft.Text(self.state.status_text, expand=True, selectable=True)
                ], visible=True),
                ft.Text("Salida: 'salida_mapeo.md' en el directorio actual.", italic=True, size=11, selectable=True)
            ],
            spacing=10,
            scroll=ft.ScrollMode.ADAPTIVE,
        )