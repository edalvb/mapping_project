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
    ):
        super().__init__()
        self.title = title
        self.tree_root = tree_root
        self.selected_paths = selected_paths
        self.on_node_toggle = on_node_toggle
        self.spacing = 8
        self.expand = True
        self.controls = self._build_content()

    def _build_tree(self, parent_tree: TreeView, node: DirectoryNode):
        is_selected = node.path in self.selected_paths

        checkbox = ft.Checkbox(
            label=node.name,
            value=is_selected,
            on_change=self.on_node_toggle,
            data=node,
        )

        child_tree = parent_tree.append(checkbox)

        for child_node in node.children:
            self._build_tree(child_tree, child_node)

    def _build_content(self):
        if not self.tree_root:
            return [
                ft.Text(self.title, style=ft.TextThemeStyle.TITLE_MEDIUM),
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
            ft.Text(self.title, style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Container(
                content=ft.Column([tree], scroll=ft.ScrollMode.ADAPTIVE, expand=True),
                expand=True,
                border=ft.border.all(1, CORTEX_AI_PALETTE.outline),
                border_radius=ft.border_radius.all(4),
                padding=ft.padding.all(10),
            ),
        ]