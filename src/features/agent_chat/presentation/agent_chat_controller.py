import flet as ft
import threading
import uuid
from typing import Callable

from ..domain.models.agent_models import (
    AgentTask,
    Author,
    ChatMessage,
    ExecutionProgress,
    ModelProvider,
    PromptStep,
)
from ..domain.services.agent_service import AgentService
from .agent_chat_state import AgentChatState


class AgentChatController:
    def __init__(
        self, 
        agent_service: AgentService, 
        state: AgentChatState,
        update_callback: Callable[[], None]
    ):
        self.agent_service = agent_service
        self.state = state
        self.update_view = update_callback

    def select_project_directory(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.state.project_directory = e.path
            self.update_view()

    def handle_user_message(self, text: str):
        if not text.strip():
            return

        user_message = ChatMessage(author=Author.USER, content=text)
        self.state.conversation.append(user_message)

        thinking_message = ChatMessage(author=Author.AGENT, content="*Pensando...*")
        self.state.conversation.append(thinking_message)
        self.update_view()

        thread = threading.Thread(
            target=self._execute_agent_response,
            args=(thinking_message,)
        )
        thread.start()

    def _execute_agent_response(self, placeholder_message: ChatMessage):
        try:
            response_text = self.agent_service.generate_interim_response(
                conversation=self.state.conversation,
                model_provider=self.state.model_provider,
                project_dir=self.state.project_directory
            )
            placeholder_message.content = response_text
        except Exception as e:
            placeholder_message.content = f"Error al procesar la respuesta: {str(e)}"
        finally:
            self.update_view()

    def update_commit_header(self, header: str):
        self.state.commit_header = header

    def update_model_provider(self, provider_name: str):
        self.state.model_provider = ModelProvider(provider_name)

    def update_prompt_step(self, step: PromptStep):
        for i, s in enumerate(self.state.prompt_steps):
            if s.id == step.id:
                self.state.prompt_steps[i] = step
                break
        self.update_view()

    def add_prompt_step(self):
        new_order = max([s.order for s in self.state.prompt_steps] + [0]) + 1
        new_step = PromptStep(
            name=f"{new_order}. Nuevo Paso",
            prompt_template="Escribe aquí tu prompt...",
            is_active=True,
            order=new_order
        )
        self.state.prompt_steps.append(new_step)
        self.update_view()
    
    def delete_prompt_step(self, step_id: uuid.UUID):
        self.state.prompt_steps = [s for s in self.state.prompt_steps if s.id != step_id]
        self.update_view()

    def start_agent_task(self):
        if self.state.progress.is_running or not self.state.project_directory:
            return
        
        task = AgentTask(
            conversation=self.state.conversation,
            prompt_steps=self.state.prompt_steps,
            commit_header=self.state.commit_header,
            model_provider=self.state.model_provider
        )

        thread = threading.Thread(
            target=self.agent_service.execute_task,
            args=(task, self.state.project_directory, self._progress_callback)
        )
        thread.start()

    def _progress_callback(self, progress: ExecutionProgress):
        self.state.progress = progress
        self.update_view()