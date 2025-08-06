import flet as ft
from typing import Callable, Optional, Set
from src.shared.presentation.theme import CORTEX_AI_PALETTE
from src.features.project_mapper.domain.models.directory_node_model import DirectoryNode
from src.shared.presentation.controls.tree_view import TreeView

class DirectorySelectionWidget(ft.Column):
    def __init__(
        self,
        title: str,
        tree_root: Optional[DirectoryNode],
        selected_paths: Set[str],
        on_node_toggle: Callable,
        on_intelligent_select: Callable,
        is_busy: bool,
    ):
        super().__init__()
        self.title = title
        self.tree_root = tree_root
        self.selected_paths = selected_paths
        self.on_node_toggle = on_node_toggle
        self.on_intelligent_select = on_intelligent_select
        self.is_busy = is_busy
        self.spacing = 8
        self.expand = True
        
        # Diccionario para mantener el estado de expansión - debe estar antes de _build_content()
        self.expansion_state = {}
        
        self.controls = self._build_content()

    def update_selected_paths(self, new_selected_paths: set):
        """Actualiza solo las rutas seleccionadas sin reconstruir el widget completo"""
        self.selected_paths = new_selected_paths
        # Actualizar todos los checkboxes sin reconstruir el árbol
        self._update_checkbox_states(self.controls)
        
        # Actualizar la página
        if self.page:
            self.page.update()

    def _update_checkbox_states(self, controls):
        """Recursivamente actualiza el estado de los checkboxes en todos los controles"""
        for control in controls:
            if isinstance(control, ft.Checkbox) and hasattr(control, 'data') and control.data:
                # Es un checkbox de selección con data del nodo
                node = control.data
                control.value = node.path in self.selected_paths
            elif hasattr(control, 'controls') and control.controls:
                # Es un contenedor con más controles, buscar recursivamente
                self._update_checkbox_states(control.controls)
            elif hasattr(control, 'content') and control.content:
                # Es un Container con contenido
                if hasattr(control.content, 'controls'):
                    self._update_checkbox_states(control.content.controls)
                elif isinstance(control.content, ft.Checkbox) and hasattr(control.content, 'data'):
                    node = control.content.data
                    if node:
                        control.content.value = node.path in self.selected_paths

    def _build_tree(self, parent_tree: TreeView, node: DirectoryNode):
        is_selected = node.path in self.selected_paths

        # Determinar el icono según el tipo de nodo
        if node.is_directory:
            icon = ft.Icons.FOLDER
            icon_color = ft.Colors.BLUE_600
        else:
            # Icono para archivos basado en la extensión
            extension = node.name.split('.')[-1].lower() if '.' in node.name else ''
            icon, icon_color = self._get_file_icon(extension)

        # Para directorios con hijos, crear controles de expansión explícitos
        if node.is_directory and node.children:
            # Estado inicial de expansión
            is_expanded = self.expansion_state.get(node.path, False)
            
            # Checkbox para la selección
            selection_checkbox = ft.Checkbox(
                value=is_selected,
                on_change=self.on_node_toggle,
                data=node,
                disabled=self.is_busy,
            )
            
            # Botón de flecha para expandir/contraer
            expand_icon = ft.Icons.KEYBOARD_ARROW_DOWN if is_expanded else ft.Icons.KEYBOARD_ARROW_RIGHT
            expand_button = ft.IconButton(
                icon=expand_icon,
                icon_size=16,
                tooltip="Expandir/Contraer carpeta",
                data=node.path,  # Para identificar qué carpeta expandir
                on_click=self._on_expand_click,
                disabled=self.is_busy,
                style=ft.ButtonStyle(
                    padding=ft.padding.all(2),
                )
            )
            
            # Contenido de la fila principal
            main_row = ft.Row(
                [
                    expand_button,
                    selection_checkbox,
                    ft.Icon(icon, color=icon_color, size=16),
                    ft.Text(
                        f"{node.name} ({len(node.children)})", 
                        size=14, 
                        weight=ft.FontWeight.W_500
                    )
                ],
                spacing=4,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            
            # Agregar la fila principal al árbol
            parent_tree.append(main_row)
            
            # Si está expandido, agregar los hijos con indentación
            if is_expanded:
                for child_node in node.children:
                    # Crear contenedor con indentación para los hijos
                    child_container = ft.Container(
                        padding=ft.padding.only(left=24),  # Indentación
                    )
                    
                    # Crear un sub-tree para este hijo
                    child_tree = TreeView(expand=True, spacing=0)
                    self._build_tree(child_tree, child_node)
                    
                    child_container.content = child_tree
                    parent_tree.append(child_container)
                
        else:
            # Para archivos o carpetas vacías
            selection_checkbox = ft.Checkbox(
                value=is_selected,
                on_change=self.on_node_toggle,
                data=node,
                disabled=self.is_busy,
            )
            
            # Contenido sin botón de expansión
            row_content = ft.Row(
                [
                    ft.Container(width=32),  # Espacio para alinear con las carpetas
                    selection_checkbox,
                    ft.Icon(icon, color=icon_color, size=16),
                    ft.Text(node.name, size=14)
                ],
                spacing=4,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )

            # Agregar al árbol sin hijos
            parent_tree.append(row_content)

    def _on_expand_click(self, e):
        """Maneja el click en el botón de expansión"""
        folder_path = e.control.data
        
        # Toggle del estado de expansión
        current_state = self.expansion_state.get(folder_path, False)
        self.expansion_state[folder_path] = not current_state
        
        # Actualizar el icono del botón inmediatamente
        if self.expansion_state[folder_path]:
            e.control.icon = ft.Icons.KEYBOARD_ARROW_DOWN
            e.control.tooltip = "Contraer carpeta"
        else:
            e.control.icon = ft.Icons.KEYBOARD_ARROW_RIGHT
            e.control.tooltip = "Expandir carpeta"
        
        # Actualizar solo el control del botón primero
        e.control.update()
        
        # Luego hacer una actualización más conservadora
        self._conservative_update()

    def _conservative_update(self):
        """Actualización conservadora que minimiza el desplazamiento"""
        # Guardar una referencia al control principal de scroll
        main_scroll_container = None
        for control in self.controls:
            if (hasattr(control, 'content') and 
                hasattr(control.content, 'controls') and
                hasattr(control.content, 'scroll')):
                main_scroll_container = control.content
                break
        
        # Reconstruir solo el contenido del árbol, no todo el widget
        if self.tree_root:
            # Crear nuevo árbol
            new_tree = TreeView(auto_collapse=True, expand=True, spacing=0)
            self._build_tree(new_tree, self.tree_root)
            
            # Reemplazar solo el contenido del árbol en el contenedor de scroll
            if main_scroll_container and hasattr(main_scroll_container, 'controls'):
                main_scroll_container.controls = [new_tree]
                
                # Actualizar solo el contenedor de scroll
                if self.page:
                    main_scroll_container.update()
            else:
                # Fallback: reconstrucción completa
                self.controls = self._build_content()
                if self.page:
                    self.page.update()
        else:
            if self.page:
                self.page.update()

    def _get_file_icon(self, extension: str) -> tuple[str, str]:
        """Retorna el icono y color apropiado para un archivo basado en su extensión"""
        icon_map = {
            'py': (ft.Icons.CODE, ft.Colors.GREEN_600),
            'js': (ft.Icons.CODE, ft.Colors.YELLOW_700),
            'ts': (ft.Icons.CODE, ft.Colors.BLUE_700),
            'dart': (ft.Icons.CODE, ft.Colors.CYAN_600),
            'java': (ft.Icons.CODE, ft.Colors.ORANGE_600),
            'cpp': (ft.Icons.CODE, ft.Colors.PURPLE_600),
            'c': (ft.Icons.CODE, ft.Colors.PURPLE_600),
            'cs': (ft.Icons.CODE, ft.Colors.BLUE_800),
            'html': (ft.Icons.WEB, ft.Colors.ORANGE_700),
            'css': (ft.Icons.STYLE, ft.Colors.BLUE_500),
            'scss': (ft.Icons.STYLE, ft.Colors.PINK_500),
            'json': (ft.Icons.DATA_OBJECT, ft.Colors.YELLOW_600),
            'xml': (ft.Icons.CODE, ft.Colors.GREY_600),
            'yaml': (ft.Icons.SETTINGS, ft.Colors.GREY_600),
            'yml': (ft.Icons.SETTINGS, ft.Colors.GREY_600),
            'md': (ft.Icons.DESCRIPTION, ft.Colors.BLUE_GREY_600),
            'txt': (ft.Icons.DESCRIPTION, ft.Colors.GREY_600),
            'pdf': (ft.Icons.PICTURE_AS_PDF, ft.Colors.RED_600),
            'png': (ft.Icons.IMAGE, ft.Colors.GREEN_500),
            'jpg': (ft.Icons.IMAGE, ft.Colors.GREEN_500),
            'jpeg': (ft.Icons.IMAGE, ft.Colors.GREEN_500),
            'gif': (ft.Icons.IMAGE, ft.Colors.GREEN_500),
            'svg': (ft.Icons.IMAGE, ft.Colors.PURPLE_500),
        }
        
        return icon_map.get(extension, (ft.Icons.INSERT_DRIVE_FILE, ft.Colors.GREY_500))

    def _build_content(self):
        header = ft.Row(
            [
                ft.Text(self.title, style=ft.TextThemeStyle.TITLE_MEDIUM, expand=True),
                ft.IconButton(
                    icon=ft.Icons.FAST_REWIND_OUTLINED,
                    tooltip="Selección Inteligente por IA",
                    on_click=self.on_intelligent_select,
                    disabled=self.is_busy,
                    icon_color=CORTEX_AI_PALETTE.tertiary
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        if not self.tree_root:
            return [
                header,
                ft.Container(
                    content=ft.Text(
                        "Seleccione un directorio de proyecto para ver las carpetas.", 
                        italic=True, 
                        color=CORTEX_AI_PALETTE.on_surface_variant
                    ),
                    expand=True,
                    border=ft.border.all(1, CORTEX_AI_PALETTE.outline),
                    border_radius=ft.border_radius.all(4),
                    padding=ft.padding.all(10),
                )
            ]

        tree = TreeView(auto_collapse=True, expand=True, spacing=0)
        self._build_tree(tree, self.tree_root)

        return [
            header,
            ft.Container(
                content=ft.Column([tree], scroll=ft.ScrollMode.ADAPTIVE, expand=True),
                expand=True,
                border=ft.border.all(1, CORTEX_AI_PALETTE.outline),
                border_radius=ft.border_radius.all(4),
                padding=ft.padding.all(10),
            ),
        ]