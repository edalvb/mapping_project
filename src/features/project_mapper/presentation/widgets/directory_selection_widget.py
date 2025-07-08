import flet as ft
from typing import Dict, Callable
from src.shared.presentation.theme import CORTEX_AI_PALETTE

class DirectorySelectionWidget(ft.Column):
    def __init__(
        self,
        title: str,
        directories: Dict[str, bool],
        on_toggle: Callable,
    ):
        super().__init__()
        self.title = title
        self.directories = directories
        self.on_toggle = on_toggle
        self.spacing = 8
        self.expand = True

        checkboxes = []
        if not self.directories:
            checkboxes.append(ft.Text("Seleccione un directorio de proyecto para ver las carpetas.", italic=True, color=CORTEX_AI_PALETTE.on_surface_variant))
        else:
            for name, is_checked in self.directories.items():
                checkboxes.append(
                    ft.Checkbox(
                        label=name,
                        value=is_checked,
                        on_change=self.on_toggle,
                        data=name,
                    )
                )

        self.controls = [
            ft.Text(self.title, style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Container(
                content=ft.ListView(controls=checkboxes, spacing=2, auto_scroll=True),
                expand=True,
                border=ft.border.all(1, CORTEX_AI_PALETTE.outline),
                border_radius=ft.border_radius.all(4),
                padding=ft.padding.all(10),
            ),
        ]
