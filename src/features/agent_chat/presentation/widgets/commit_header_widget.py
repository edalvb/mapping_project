import flet as ft
from typing import Callable

class CommitHeaderWidget(ft.TextField):
    def __init__(self, on_change: Callable[[str], None]):
        super().__init__(
            label="Commit Header (optional)",
            hint_text="refactor/obs120625:",
            on_change=self._handle_change,
            border_radius=ft.border_radius.all(8),
            dense=True,
        )
        self.on_change_handler = on_change

    def _handle_change(self, e):
        self.on_change_handler(e.control.value)
