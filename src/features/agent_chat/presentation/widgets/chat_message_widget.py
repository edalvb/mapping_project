import flet as ft
from ...domain.models.agent_models import Author, ChatMessage
from .....core import theme

class ChatMessageWidget(ft.Row):
    def __init__(self, message: ChatMessage):
        super().__init__()
        self.message = message
        is_user = self.message.author == Author.USER

        author_icon = ft.Icon(
            name=ft.Icons.PERSON if is_user else ft.Icons.COMPUTER_ROUNDED,
            color=theme.on_surface,
            size=24
        )

        message_content = ft.Markdown(
            self.message.content,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme=ft.MarkdownCustomCodeTheme(),
            on_tap_link=lambda e: self.page.launch_url(e.data)
        )
        
        message_container = ft.Container(
            content=message_content,
            padding=ft.padding.all(12),
            border_radius=ft.border_radius.all(12),
            bgcolor=theme.primary_container if is_user else theme.secondary_container,
            margin=ft.margin.only(top=5, bottom=5),
            alignment=ft.alignment.top_left,
            expand=True,
        )

        copy_button = ft.IconButton(
            icon=ft.Icons.COPY_ALL_OUTLINED,
            icon_size=16,
            tooltip="Copiar al portapapeles",
            on_click=self._copy_to_clipboard
        )

        if is_user:
            self.alignment = ft.MainAxisAlignment.END
            self.controls = [
                ft.Column([message_container], expand=True, horizontal_alignment=ft.CrossAxisAlignment.END),
                ft.Column([author_icon, copy_button], spacing=5)
            ]
        else:
            self.controls = [
                ft.Column([author_icon, copy_button], spacing=5),
                ft.Column([message_container], expand=True)
            ]
            
    def _copy_to_clipboard(self, e):
        if not self.page:
            return
        self.page.set_clipboard(self.message.content)
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Mensaje copiado al portapapeles"),
            duration=2000
        )
        self.page.snack_bar.open = True
        self.page.update()
