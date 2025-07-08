import math
import flet as ft
from src.features.project_mapper.presentation.project_mapper_controller import ProjectMapperController
from src.features.project_mapper.presentation.project_mapper_state import ProjectMapperState
from src.features.project_mapper.presentation.widgets.extensions_list_widget import ExtensionsListWidget
from src.features.project_mapper.presentation.widgets.directory_selection_widget import DirectorySelectionWidget
from src.shared.presentation.theme import CORTEX_AI_PALETTE

class ProjectMapperView(ft.Row):
    def __init__(self, controller: ProjectMapperController, state: ProjectMapperState):
        super().__init__()
        self.controller = controller
        self.state = state
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.spacing = 20

    def did_mount(self):
        self.update_view()

    def update_view(self):
        self.controls = self._build_content()
        if self.page: self.page.update()

    def _build_content(self):
        left_panel = ft.Container(
            content=ft.Column(
                [
                    DirectorySelectionWidget(
                        title="Carpetas a Mapear",
                        directories=self.state.subdirectories,
                        on_toggle=self.controller.on_toggle_directory,
                    ),
                    ft.Tabs(
                        selected_index=0,
                        animation_duration=300,
                        tabs=[
                            ft.Tab(
                                text="Incluir",
                                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                                content=ExtensionsListWidget(
                                    title="Extensiones a incluir (ej: .py)",
                                    items=sorted(list(self.state.include_extensions)),
                                    new_item_value=self.state.new_include_extension,
                                    on_add=self.controller.add_include_extension,
                                    on_delete=self.controller.delete_include_extension,
                                    on_change_new_item=self.controller.on_change_include_text,
                                    on_submit_new_item=self.controller.add_include_extension
                                )
                            ),
                            ft.Tab(
                                text="Excluir",
                                icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                                content=ExtensionsListWidget(
                                    title="Patrones a excluir (ej: .g.dart)",
                                    items=sorted(list(self.state.exclude_patterns)),
                                    new_item_value=self.state.new_exclude_pattern,
                                    on_add=self.controller.add_exclude_pattern,
                                    on_delete=self.controller.delete_exclude_pattern,
                                    on_change_new_item=self.controller.on_change_exclude_text,
                                    on_submit_new_item=self.controller.add_exclude_pattern
                                )
                            )
                        ],
                        expand=True
                    )
                ],
                spacing=10,
            ),
            expand=5, # 50% width
            padding=ft.padding.only(right=10)
        )

        right_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Configuración de Salida", style=ft.TextThemeStyle.HEADLINE_SMALL),
                    ft.Row([
                        ft.ElevatedButton("Seleccionar Proyecto", icon=ft.Icons.FOLDER_OPEN, on_click=self.controller.pick_project_dir, expand=True),
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Text(self.state.project_dir_path or "Ruta no seleccionada", no_wrap=True, selectable=True),
                    ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                    ft.Row([
                            ft.ElevatedButton("Carpeta de Salida", icon=ft.Icons.SAVE_AS, on_click=self.controller.pick_output_dir, expand=True),
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Text(self.state.output_dir_path or "Carpeta no seleccionada", no_wrap=True, selectable=True),
                    ft.TextField(
                        label="Nombre del Archivo de Salida",
                        value=self.state.output_filename,
                        on_change=self.controller.on_change_output_filename,
                        hint_text="Ej: nombre_proyecto.md",
                    ),
                    ft.Divider(height=20),
                    ft.ElevatedButton(
                        "Iniciar Mapeo",
                        icon=ft.Icons.DOCUMENT_SCANNER,
                        on_click=self.controller.start_mapping_process,
                        bgcolor=CORTEX_AI_PALETTE.primary,
                        color=CORTEX_AI_PALETTE.on_primary,
                        disabled=self.state.is_loading,
                        width=math.inf
                    ),
                    ft.Row([
                        ft.ProgressRing(width=16, height=16, stroke_width=2, visible=self.state.is_loading),
                        ft.Text(self.state.status_text, expand=True, selectable=True)
                    ], visible=True),
                    ft.Text("El archivo de salida se guardará en la ruta especificada.", italic=True, size=11, selectable=True)
                ],
                spacing=10,
                scroll=ft.ScrollMode.ADAPTIVE
            ),
            expand=5, # 50% width
            padding=ft.padding.only(left=10)
        )

        return [
            left_panel,
            ft.VerticalDivider(width=1),
            right_panel
        ]
