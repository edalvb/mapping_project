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

        if is_user:
            self.alignment = ft.MainAxisAlignment.END
            self.controls = [
                ft.Column([message_container], expand=True, horizontal_alignment=ft.CrossAxisAlignment.END),
                author_icon
            ]
        else:
            self.controls = [
                author_icon,
                ft.Column([message_container], expand=True)
            ]
