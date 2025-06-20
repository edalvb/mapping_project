import flet as ft
from .agent_chat_controller import AgentChatController
from .agent_chat_state import AgentChatState
from ..domain.models.agent_models import ModelProvider
from .widgets.chat_input_bar_widget import ChatInputBarWidget
from .widgets.chat_message_widget import ChatMessageWidget
from .widgets.agent_prompt_settings_widget import AgentPromptSettingsWidget
from .widgets.commit_header_widget import CommitHeaderWidget
from ....core import theme

class AgentChatPage(ft.Row):
    def __init__(self, controller: AgentChatController, state: AgentChatState):
        super().__init__()
        self.controller = controller
        self.state = state
        
        self.chat_history_view = ft.ListView(expand=True, auto_scroll=True, spacing=10)
        self.progress_bar = ft.ProgressBar(value=0, bar_height=5)
        self.progress_text = ft.Text("Idle", size=12)
        
        self.start_button = ft.FilledButton("Start Agent", icon=ft.Icons.PLAY_ARROW, on_click=lambda _: self.controller.start_agent_task())
        self.stop_button = ft.OutlinedButton("Stop Agent", icon=ft.Icons.STOP_CIRCLE_OUTLINED, on_click=lambda _: self.controller.stop_current_task(), visible=False, icon_color=theme.error)
        
        self.project_dir_text = ft.Text("No seleccionado", italic=True, size=12, expand=True)

        self.prompt_settings = AgentPromptSettingsWidget(
            steps=self.state.prompt_steps,
            on_update_step=self.controller.update_prompt_step,
            on_add_step=self.controller.add_prompt_step,
            on_delete_step=self.controller.delete_prompt_step
        )

        model_provider_dropdown = ft.Dropdown(
            label="Modelo de IA",
            value=self.state.model_provider.value,
            options=[
                ft.dropdown.Option(provider.value) for provider in ModelProvider
            ],
            on_change=lambda e: self.controller.update_model_provider(e.control.value)
        )

        chat_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        controls=[
                            ft.Text("Conversación", style=ft.TextThemeStyle.TITLE_LARGE, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_SWEEP_OUTLINED,
                                tooltip="Limpiar chat",
                                on_click=lambda _: self.controller.clear_chat_conversation()
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(),
                    self.chat_history_view,
                    ft.Column([self.progress_bar, self.progress_text], spacing=5),
                    ChatInputBarWidget(
                        on_submit=self.controller.handle_user_message, 
                        on_files_selected=lambda f: print("Files selected, logic to be implemented")
                    )
                ],
                expand=True
            ),
            expand=True,
            padding=ft.padding.all(15)
        )

        settings_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Configuración de Tarea", style=ft.TextThemeStyle.TITLE_LARGE),
                    ft.Divider(),
                    ft.Row([
                        ft.ElevatedButton(
                            "Directorio del Proyecto", 
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=lambda _: self.file_picker.get_directory_path()
                        ),
                        self.project_dir_text
                    ]),
                    model_provider_dropdown,
                    CommitHeaderWidget(on_change=self.controller.update_commit_header),
                    ft.Divider(height=20),
                    self.prompt_settings,
                    ft.Stack([self.start_button, self.stop_button])
                ],
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            width=450,
            padding=ft.padding.all(20),
            border=ft.border.only(left=ft.BorderSide(1, theme.outline_variant))
        )

        self.controls = [chat_panel, settings_panel]
        self.expand = True

    def did_mount(self):
        self.file_picker = ft.FilePicker(on_result=self.controller.select_project_directory)
        self.page.overlay.append(self.file_picker)
        self.page.update()

    def update_view(self):
        if not self.page or not self.page.client_storage:
            return

        self.chat_history_view.controls = [
            ChatMessageWidget(msg) for msg in self.state.conversation
        ]
        
        is_running = self.state.progress.is_running
        self.progress_bar.value = (
            (self.state.progress.current_step / self.state.progress.total_steps)
            if self.state.progress.total_steps > 0
            else (1.0 if is_running else 0)
        )
        self.progress_bar.color = theme.secondary if self.state.progress.total_steps > 0 else theme.tertiary
        self.progress_text.value = self.state.progress.message
        
        self.start_button.visible = not is_running
        self.stop_button.visible = is_running
        self.start_button.disabled = not self.state.project_directory

        self.prompt_settings.update_steps(self.state.prompt_steps)
        self.project_dir_text.value = self.state.project_directory or "No seleccionado"

        self.update()
