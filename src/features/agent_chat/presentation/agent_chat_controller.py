import flet as ft
import threading
import uuid
from typing import Callable, Optional

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
        self.current_stop_event: Optional[threading.Event] = None

    def select_project_directory(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.state.project_directory = e.path
            self.update_view()

    def handle_user_message(self, text: str):
        if not text.strip() or self.state.progress.is_running:
            return

        user_message = ChatMessage(author=Author.USER, content=text)
        self.state.conversation.append(user_message)

        thinking_message = ChatMessage(author=Author.AGENT, content="*Pensando...*")
        self.state.conversation.append(thinking_message)
        
        self.state.progress.is_running = True
        self.state.progress.message = "Generando respuesta..."
        self.update_view()
        
        self.current_stop_event = threading.Event()
        thread = threading.Thread(
            target=self._execute_agent_response,
            args=(thinking_message, self.current_stop_event)
        )
        thread.start()

    def clear_chat_conversation(self):
        self.state.conversation.clear()
        self.update_view()

    def _execute_agent_response(self, placeholder_message: ChatMessage, stop_event: threading.Event):
        try:
            response_text = self.agent_service.generate_interim_response(
                conversation=self.state.conversation,
                model_provider=self.state.model_provider,
                project_dir=self.state.project_directory,
                stop_event=stop_event
            )
            if response_text is not None:
                placeholder_message.content = response_text
            else:
                placeholder_message.content = "*Operación cancelada por el usuario.*"
        except Exception as e:
            placeholder_message.content = f"Error al procesar la respuesta: {str(e)}"
        finally:
            self.state.progress.is_running = False
            self.state.progress.message = "Idle"
            self.current_stop_event = None
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
        
        self.current_stop_event = threading.Event()
        thread = threading.Thread(
            target=self.agent_service.execute_task,
            args=(task, self.state.project_directory, self._progress_callback, self.current_stop_event)
        )
        thread.start()

    def stop_current_task(self):
        if self.current_stop_event:
            self.current_stop_event.set()

    def _progress_callback(self, progress: ExecutionProgress):
        self.state.progress = progress
        if not progress.is_running:
            self.current_stop_event = None
        self.update_view()
