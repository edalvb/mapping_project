import flet as ft
from typing import List, Callable
from src.shared.presentation.theme import CORTEX_AI_PALETTE

class ExtensionsListWidget(ft.Column):
    def __init__(
        self,
        title: str,
        items: List[str],
        new_item_value: str,
        on_add: Callable,
        on_delete: Callable,
        on_change_new_item: Callable,
        on_submit_new_item: Callable,
    ):
        super().__init__()
        self.title = title
        self.items = items
        self.new_item_value = new_item_value
        self.on_add = on_add
        self.on_delete = on_delete
        self.on_change_new_item = on_change_new_item
        self.on_submit_new_item = on_submit_new_item

        list_view_controls = []
        for item in self.items:
            list_view_controls.append(
                ft.Row(
                    [
                        ft.Text(item, expand=True),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            tooltip=f"Eliminar {item}",
                            on_click=self.on_delete,
                            data=item,
                            icon_color=CORTEX_AI_PALETTE.error,
                            icon_size=18,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
        
        self.expand = True
        self.spacing = 8
        self.controls = [
            ft.Text(self.title),
            ft.Row([
                ft.TextField(
                    value=self.new_item_value,
                    on_change=self.on_change_new_item,
                    label=self.title.split(' ')[-1].strip('():'),
                    expand=True,
                    dense=True,
                    on_submit=self.on_submit_new_item,
                ),
                ft.ElevatedButton("Agregar", icon=ft.Icons.ADD, on_click=self.on_add),
            ]),
            ft.Text("Lista:"),
            ft.Container(
                content=ft.ListView(controls=list_view_controls, spacing=2, auto_scroll=True),
                expand=True,
                border=ft.border.all(1, CORTEX_AI_PALETTE.outline),
                border_radius=ft.border_radius.all(4),
                padding=ft.padding.all(5),
            ),
        ]