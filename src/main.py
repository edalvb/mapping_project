import flet as ft

from src.core.config import get_settings
from src.core.theme import cortex_theme
from src.features.agent_chat.data.repositories.gemini_repository import GeminiRepository
from src.features.agent_chat.data.repositories.langchain_repository import LangchainRepository
from src.features.agent_chat.data.repositories.local_fs_repository import LocalFsRepository
from src.features.agent_chat.data.repositories.project_mapper_repository import ProjectMapperRepository
from src.features.agent_chat.domain.models.agent_models import ModelProvider, PromptStep
from src.features.agent_chat.domain.services.agent_service import AgentService
from src.features.agent_chat.presentation.agent_chat_controller import AgentChatController
from src.features.agent_chat.presentation.agent_chat_page import AgentChatPage
from src.features.agent_chat.presentation.agent_chat_state import AgentChatState

def get_default_prompts() -> list[PromptStep]:
    return [
        PromptStep(
            order=1,
            name="1. Analizar Tarea",
            prompt_template='''Tu tarea es analizar la siguiente conversación y el mapa del proyecto para determinar la mejor estrategia de implementación. Describe los pasos necesarios de forma clara y concisa.\n\nCONVERSACIÓN:\n{conversation}\n\nMAPA DEL PROYECTO:\n{project_map}'''
        ),
        PromptStep(
            order=2,
            name="2. Listar Archivos Accionables (JSON)",
            prompt_template='''Basado en el análisis y la conversación, lista TODOS los archivos que se deben crear, modificar o eliminar para completar la tarea. Devuelve la lista en formato JSON, ordenada por dependencia.\n\nFormato de salida OBLIGATORIO:\n```json\n[ { "path": "path/to/file1.ext", "order": 1 }, { "path": "path/to/file2.ext", "order": 2 } ]\n```\n\nCONVERSACIÓN:\n{conversation}\n\nMAPA DEL PROYECTO:\n{project_map}\n\nANÁLISIS PREVIO:\n{1._analizar_tarea_result}'''
        ),
        PromptStep(
            order=3,
            name="3. Generar Código por Lote",
            prompt_template='''La aplicación debe tener un diseño limpio y moderno, utilizando los colores de la marca. Genera todos los archivos y la estructura necesarios para que la aplicación funcione correctamente. El código debe ser completamente autoexplicativo, por lo tanto, NO INCLUYAS NINGÚN COMENTARIO EN EL CÓDIGO FUENTE. Aplica rigurosamente los principios SOLID y sigue las mejores prácticas de programación para asegurar que el código sea limpio, eficiente, sin redundancias, libre de errores, fácil de mantener y escalable en el futuro. El código entregado debe ser funcional y no contener secciones comentadas inactivas. Además NO AÑADAS loggers.\n\nAquí está la lista de archivos que debes generar o modificar en este lote:\n{file_list}\n\nUsa el siguiente mapa del proyecto y la conversación como contexto completo.\n\nMAPA DEL PROYECTO:\n{project_map}\n\nCONVERSACIÓN:\n{conversation}\n\nFormato de salida OBLIGATORIO:\n```json\n[ { "path": "path/to/file1.ext", "content": "<código completo aquí>" }, { "path": "path/to/file2.ext", "content": "<código completo aquí>" } ]\n```'''
        ),
        PromptStep(
            order=4,
            name="4. Generar Mensaje de Commit",
            prompt_template='''Basado en los cambios realizados (reflejados en el mapa del proyecto) y la conversación, genera un mensaje de commit en inglés. El formato debe ser: {commit_header}<título conciso en imperativo>\n\n<descripción opcional de los cambios>.\n\nMAPA DEL PROYECTO FINAL:\n{project_map}\n\nCONVERSACIÓN:\n{conversation}'''
        ),
    ]

def main(page: ft.Page):
    page.title = "Cortex AI Agent"
    page.theme = cortex_theme
    page.window_width = 1400
    page.window_height = 900
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    try:
        settings = get_settings()
    except Exception as e:
        page.add(ft.Text(f"Error al cargar configuración: {e}. Asegúrate de tener un archivo .env."))
        return

    llm_repositories = {}
    if settings.OPENAI_API_KEY:
        llm_repositories[ModelProvider.OPENAI] = LangchainRepository(settings)
    if settings.GOOGLE_API_KEY:
        llm_repositories[ModelProvider.GEMINI] = GeminiRepository(settings)

    if not llm_repositories:
        page.add(ft.Text("Error: No se encontró ninguna clave de API (OPENAI_API_KEY o GOOGLE_API_KEY) en el archivo .env."))
        return

    fs_repo = LocalFsRepository()
    mapper_repo = ProjectMapperRepository()

    agent_service = AgentService(
        llm_repositories=llm_repositories,
        file_system_repository=fs_repo,
        project_mapper_repository=mapper_repo,
    )

    initial_state = AgentChatState(
        prompt_steps=get_default_prompts(),
        model_provider=next(iter(llm_repositories.keys()))
    )

    def update_view_handler():
        if agent_chat_page:
            agent_chat_page.update_view()

    agent_chat_controller = AgentChatController(
        agent_service=agent_service,
        state=initial_state,
        update_callback=update_view_handler,
    )

    agent_chat_page = AgentChatPage(
        controller=agent_chat_controller,
        state=initial_state
    )

    page.add(agent_chat_page)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
