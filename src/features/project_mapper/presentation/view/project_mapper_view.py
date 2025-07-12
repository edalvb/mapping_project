import math
import flet as ft
from src.features.project_mapper.presentation.project_mapper_controller import ProjectMapperController
from src.features.project_mapper.presentation.project_mapper_state import ProjectMapperState
from src.features.project_mapper.presentation.widgets.extensions_list_widget import ExtensionsListWidget
from src.features.project_mapper.presentation.widgets.directory_selection_widget import DirectorySelectionWidget
from src.features.project_mapper.presentation.widgets.ai_selection_config_widget import AISelectionConfigWidget
from src.shared.presentation.theme import CORTEX_AI_PALETTE

class ProjectMapperView(ft.Row):
    def __init__(self, controller: ProjectMapperController, state: ProjectMapperState):
        super().__init__()
        self.controller = controller
        self.state = state
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.spacing = 20
        self.expand = True

        self.left_panel = ft.Container(
            expand=1,
            padding=ft.padding.only(right=10)
        )

        self.right_tabs = ft.Tabs(
            on_change=self.controller.on_tab_change,
            animation_duration=300,
            expand=True
        )

        self.right_panel = ft.Container(
            content=self.right_tabs,
            expand=1,
            padding=ft.padding.only(left=10)
        )

        self.controls = [self.left_panel, ft.VerticalDivider(width=1), self.right_panel]

    def did_mount(self):
        self.controller.on_view_did_mount()
        self.update_view()

    def update_view(self):
        is_busy = self.state.is_loading or self.state.is_ai_selecting

        self.left_panel.content = DirectorySelectionWidget(
            title="Carpetas a Mapear",
            tree_root=self.state.directory_tree,
            selected_paths=self.state.selected_dirs,
            on_node_toggle=self.controller.on_directory_toggle,
            on_intelligent_select=self.controller.start_intelligent_selection,
            is_busy=is_busy,
        )

        self.right_tabs.selected_index = self.state.right_panel_tab_index
        self.right_tabs.tabs = self._build_right_tabs(is_busy)

        if self.page: self.page.update()

    def _build_config_panel(self, is_busy):
        return ft.Column(
            [
                ft.Text("Configuración de Salida", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.ElevatedButton("Seleccionar Proyecto", icon=ft.Icons.FOLDER_OPEN, on_click=self.controller.pick_project_dir, disabled=is_busy),
                ft.Text(self.state.project_dir_path or "Ruta no seleccionada", no_wrap=True, selectable=True),
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                ft.ElevatedButton("Carpeta de Salida", icon=ft.Icons.SAVE_AS, on_click=self.controller.pick_output_dir, disabled=is_busy),
                ft.Text(self.state.output_dir_path or "Carpeta no seleccionada", no_wrap=True, selectable=True),
                ft.TextField(
                    label="Nombre del Archivo de Salida",
                    value=self.state.output_filename,
                    on_change=self.controller.on_change_output_filename,
                    hint_text="Ej: nombre_proyecto.md",
                    disabled=is_busy,
                ),
                ft.Divider(height=20),
                ft.ElevatedButton(
                    "Iniciar Mapeo Manual",
                    icon=ft.Icons.DOCUMENT_SCANNER,
                    on_click=self.controller.start_mapping_process,
                    bgcolor=CORTEX_AI_PALETTE.primary,
                    color=CORTEX_AI_PALETTE.on_primary,
                    disabled=is_busy,
                    width=math.inf,
                ),
                ft.Row([
                    ft.ProgressRing(width=16, height=16, stroke_width=2, visible=self.state.is_loading),
                    ft.Text(self.state.status_text, expand=True, selectable=True)
                ]),
            ],
            spacing=10,
            scroll=ft.ScrollMode.ADAPTIVE
        )

    def _build_right_tabs(self, is_busy):
        config_panel = self._build_config_panel(is_busy)

        ai_config_widget = AISelectionConfigWidget(
            api_key=self.state.llm_api_key,
            models_loaded=self.state.llm_models_loaded,
            available_models=self.state.available_llm_models,
            selected_model=self.state.selected_llm_model,
            system_instruction=self.state.llm_system_instruction,
            objective=self.state.llm_objective,
            is_ai_selecting=self.state.is_ai_selecting,
            ai_status_text=self.state.ai_status_text,
            on_change_api_key=self.controller.on_change_llm_api_key,
            on_verify_api_key=self.controller.verify_and_load_models,
            on_change_model=self.controller.on_change_selected_model,
            on_change_instruction=self.controller.on_change_llm_system_instruction,
            on_change_objective=self.controller.on_change_llm_objective,
        )

        include_widget = ExtensionsListWidget(
            title="Extensiones a incluir (ej: .py)", items=sorted(list(self.state.include_extensions)), 
            new_item_value=self.state.new_include_extension, on_add=self.controller.add_include_extension, 
            on_delete=self.controller.delete_include_extension, on_change_new_item=self.controller.on_change_include_text, 
            on_submit_new_item=self.controller.add_include_extension
        )

        exclude_widget = ExtensionsListWidget(
            title="Patrones a excluir (ej: .g.dart)", items=sorted(list(self.state.exclude_patterns)), 
            new_item_value=self.state.new_exclude_pattern, on_add=self.controller.add_exclude_pattern, 
            on_delete=self.controller.delete_exclude_pattern, on_change_new_item=self.controller.on_change_exclude_text, 
            on_submit_new_item=self.controller.add_exclude_pattern
        )

        return [
            ft.Tab(text="Configuración", icon=ft.Icons.SETTINGS, content=config_panel),
            ft.Tab(text="Selección por IA", icon=ft.Icons.AUTO_AWESOME, content=ai_config_widget),
            ft.Tab(text="Incluir", icon=ft.Icons.ADD_CIRCLE_OUTLINE, content=include_widget),
            ft.Tab(text="Excluir", icon=ft.Icons.REMOVE_CIRCLE_OUTLINE, content=exclude_widget),
        ]
