import flet as ft
from typing import Callable, List
from .....core import theme

class ChatInputBarWidget(ft.Container):
    def __init__(
        self,
        on_submit: Callable[[str], None],
        on_files_selected: Callable[[List[ft.FilePickerResultEvent]], None]
    ):
        super().__init__()
        self.on_submit_handler = on_submit
        self.on_files_selected_handler = on_files_selected
        
        self.text_field = ft.TextField(
            hint_text="Describe la tarea o envía un mensaje...",
            multiline=True,
            min_lines=1,
            max_lines=12,
            shift_enter=True,
            on_submit=self._submit_message,
            expand=True,
            border_radius=ft.border_radius.all(12),
            border_color=ft.Colors.with_opacity(0.5, theme.outline_variant)
        )

        attachment_menu = ft.PopupMenuButton(
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            items=[
                ft.PopupMenuItem(
                    text="Adjuntar Archivos",
                    icon=ft.Icons.ATTACH_FILE,
                    on_click=self._pick_files
                ),
                ft.PopupMenuItem(
                    text="Adjuntar desde Google Drive",
                    icon=ft.Icons.CLOUD_UPLOAD,
                    on_click=self._show_future_feature_snackbar
                ),
            ]
        )

        send_button = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            tooltip="Enviar Mensaje",
            on_click=self._submit_message,
            bgcolor=theme.primary,
            icon_color=theme.on_primary,
        )

        self.padding = ft.padding.symmetric(vertical=10, horizontal=15)
        self.content = ft.Row(
            controls=[
                attachment_menu,
                self.text_field,
                send_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def did_mount(self):
        self.file_picker = ft.FilePicker(on_result=self._on_picker_result)
        self.page.overlay.append(self.file_picker)
        self.page.update()

    def _pick_files(self, e):
        self.file_picker.pick_files(allow_multiple=True)

    def _submit_message(self, e):
        text = self.text_field.value.strip()
        if text:
            self.on_submit_handler(text)
            self.text_field.value = ""
            self.update()

    def _on_picker_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.on_files_selected_handler(e.files)

    def _show_future_feature_snackbar(self, e):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("La integración con Google Drive se implementará en una versión futura."),
            open=True
        )
        self.page.update()
