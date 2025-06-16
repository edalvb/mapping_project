import flet as ft
from typing import Callable, List
import uuid

from ...domain.models.agent_models import PromptStep
from .....core import theme

class _PromptStepRow(ft.Container):
    def __init__(self, step: PromptStep, on_update: Callable, on_delete: Callable):
        super().__init__()
        self.step = step
        self.on_update_handler = on_update
        self.on_delete_handler = on_delete

        self.name_field = ft.TextField(
            value=self.step.name,
            on_change=self._handle_name_change,
            border=ft.InputBorder.NONE,
            expand=True,
            text_size=14,
        )
        
        self.padding = ft.padding.symmetric(vertical=5, horizontal=8)
        self.border = ft.border.all(1, theme.outline_variant)
        self.border_radius = ft.border_radius.all(8)
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Checkbox(
                    value=self.step.is_active,
                    on_change=self._handle_active_change,
                ),
                self.name_field,
                ft.IconButton(
                    icon=ft.Icons.EDIT_DOCUMENT,
                    tooltip="Editar plantilla del prompt",
                    on_click=self._open_edit_dialog,
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_FOREVER,
                    icon_color=theme.error,
                    tooltip="Eliminar paso",
                    on_click=self._handle_delete,
                ),
            ]
        )

    def _handle_active_change(self, e):
        self.step.is_active = e.control.value
        self.on_update_handler(self.step)

    def _handle_name_change(self, e):
        self.step.name = e.control.value
        self.on_update_handler(self.step)

    def _handle_delete(self, e):
        self.on_delete_handler(self.step.id)

    def _open_edit_dialog(self, e):
        template_field = ft.TextField(
            value=self.step.prompt_template,
            multiline=True,
            min_lines=15,
            max_lines=25,
            expand=True,
        )

        def save_changes(e):
            self.step.prompt_template = template_field.value
            self.on_update_handler(self.step)
            self.page.dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Editar Prompt: {self.step.name}"),
            content=ft.Container(content=template_field, width=800, height=500),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(self.page.dialog, 'open', False) or self.page.update()),
                ft.FilledButton("Guardar", on_click=save_changes),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()

class AgentPromptSettingsWidget(ft.Container):
    def __init__(
        self,
        steps: List[PromptStep],
        on_update_step: Callable[[PromptStep], None],
        on_add_step: Callable[[], None],
        on_delete_step: Callable[[uuid.UUID], None],
    ):
        super().__init__()
        self._steps = steps
        self._on_update_step = on_update_step
        self._on_add_step = on_add_step
        self._on_delete_step = on_delete_step

        self.prompt_list_view = ft.Column(
            controls=self._build_step_rows(),
            spacing=10,
            scroll=ft.ScrollMode.ADAPTIVE
        )

        self.padding = 15
        self.border = ft.border.all(1, theme.outline_variant)
        self.border_radius = ft.border_radius.all(12)
        self.expand = True
        self.content = ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.Text("Pasos de Ejecución del Agente", style=ft.TextThemeStyle.TITLE_MEDIUM, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.ADD_BOX_ROUNDED,
                            tooltip="Añadir nuevo paso",
                            on_click=lambda _: self._on_add_step()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                self.prompt_list_view
            ],
            expand=True
        )

    def update_steps(self, new_steps: List[PromptStep]):
        self._steps = new_steps
        self.prompt_list_view.controls = self._build_step_rows()
        self.update()

    def _build_step_rows(self) -> List[ft.Control]:
        return [
            _PromptStepRow(
                step=s,
                on_update=self._on_update_step,
                on_delete=self._on_delete_step,
            ) for s in sorted(self._steps, key=lambda x: x.order)
        ]
