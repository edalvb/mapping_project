import json
import re
from typing import Callable, Dict, List, Optional

from ...data.dto.code_generation_dto import FileContentList
from ..models.agent_models import AgentTask, Author, ChatMessage, ExecutionProgress, ModelProvider
from ..repositories.i_file_system_repository import IFileSystemRepository
from ..repositories.i_llm_repository import ILLMRepository
from ..repositories.i_project_mapper_repository import IProjectMapperRepository


class AgentService:
    def __init__(
        self,
        llm_repositories: Dict[ModelProvider, ILLMRepository],
        file_system_repository: IFileSystemRepository,
        project_mapper_repository: IProjectMapperRepository,
    ):
        self._llm_repos = llm_repositories
        self._fs_repo = file_system_repository
        self._mapper_repo = project_mapper_repository

    def generate_interim_response(
        self, 
        conversation: List[ChatMessage], 
        model_provider: ModelProvider,
        project_dir: Optional[str]
    ) -> str:
        llm_repo = self._get_llm_repository(model_provider)
        
        prompt_template = """Eres Cortex, un asistente de desarrollo de IA de élite. La siguiente es una conversación con un usuario y el mapa del proyecto actual. Tu tarea es proporcionar una respuesta breve, útil y contextual. Confirma que entiendes la última solicitud del usuario y anímale a usar el botón 'Start Agent' para comenzar la ejecución de la tarea principal. No generes código. Sé conciso.

CONVERSACIÓN:
{conversation_history}

MAPA DEL PROYECTO:
{project_map}"""

        if project_dir and self._fs_repo.is_directory(project_dir):
            project_map = self._mapper_repo.map_project_to_string(project_dir, [], [])
        else:
            project_map = "El directorio del proyecto aún no ha sido seleccionado."

        conversation_history = "\n".join([f"{msg.author.value}: {msg.content}" for msg in conversation])
        context = {
            "conversation_history": conversation_history,
            "project_map": project_map
        }

        response = llm_repo.execute_prompt(prompt_template, context)
        return response

    def execute_task(
        self,
        task: AgentTask,
        project_dir: str,
        progress_callback: Callable[[ExecutionProgress], None],
    ):
        progress = ExecutionProgress(is_running=True)
        try:
            llm_repo = self._get_llm_repository(task.model_provider)
            context = self._initialize_context(task, project_dir)
            self._run_pipeline(task, context, progress, progress_callback, project_dir, llm_repo)
        except Exception as e:
            progress.message = f"An error occurred: {str(e)}"
        finally:
            progress.is_running = False
            progress_callback(progress)

    def _get_llm_repository(self, provider: ModelProvider) -> ILLMRepository:
        repo = self._llm_repos.get(provider)
        if not repo:
            raise ValueError(f"LLM provider {provider.value} is not configured.")
        return repo

    def _run_pipeline(
        self,
        task: AgentTask,
        context: Dict[str, str],
        progress: ExecutionProgress,
        progress_callback: Callable[[ExecutionProgress], None],
        project_dir: str,
        llm_repo: ILLMRepository,
    ):
        active_steps = sorted([s for s in task.prompt_steps if s.is_active], key=lambda s: s.order)
        if not active_steps:
            progress.message = "No active steps to execute."
            return

        total_steps = len(active_steps)
        progress.total_steps = total_steps

        step_results = {}

        for i, step in enumerate(active_steps):
            progress.current_step = i + 1
            progress.message = f"Executing step {i+1}/{total_steps}: {step.name}"
            progress_callback(progress)

            step_context = context.copy()
            step_context.update(step_results)

            if "Generar Código por Lote" in step.name:
                self._process_code_generation(
                    step.prompt_template, step_context, progress, progress_callback, project_dir, llm_repo
                )
            else:
                result = llm_repo.execute_prompt(step.prompt_template, step_context)
                result_key = f"{step.name.lower().replace(' ', '_').replace('.', '').replace('(', '').replace(')', '')}_result"
                step_results[result_key] = result
                context[result_key] = result
        
        progress.message = "Task completed successfully."
        progress.current_step = total_steps

    def _process_code_generation(
        self, template: str, context: Dict[str, str],
        progress: ExecutionProgress, progress_callback: Callable[[ExecutionProgress], None],
        project_dir: str, llm_repo: ILLMRepository
    ):
        file_list_json_str = context.get("2_listar_archivos_accionables_json_result", "[]")
        work_queue = self._parse_file_list(file_list_json_str)
        if not work_queue:
            return
            
        batches = [work_queue[i:i + 2] for i in range(0, len(work_queue), 2)]

        for i, batch in enumerate(batches):
            progress.message = f"Generating code for batch {i+1}/{len(batches)}"
            progress_callback(progress)

            batch_context = context.copy()
            batch_context["file_list"] = "\n".join([f"- {item['path']}" for item in batch])

            code_json_str = llm_repo.execute_prompt(template, batch_context)
            
            cleaned_json_str = self._clean_json_string(code_json_str)
            file_contents = FileContentList.model_validate_json(cleaned_json_str)
            
            for file_content in file_contents.root:
                self._fs_repo.write_file(file_content.path, file_content.content)

            context["project_map"] = self._mapper_repo.map_project_to_string(project_dir, [], [])
            progress_callback(progress)

    def _initialize_context(self, task: AgentTask, project_dir: str) -> Dict[str, str]:
        if not self._fs_repo.is_directory(project_dir):
            project_map = "Project directory not selected or does not exist."
        else:
            project_map = self._mapper_repo.map_project_to_string(project_dir, [], [])

        conversation_history = "\n".join([f"{msg.author.value}: {msg.content}" for msg in task.conversation])
        
        return {
            "project_map": project_map,
            "conversation": conversation_history,
            "commit_header": task.commit_header or ""
        }

    def _parse_file_list(self, json_str: str) -> List[Dict[str, str]]:
        try:
            cleaned_json = self._clean_json_string(json_str)
            data = json.loads(cleaned_json)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []
            
    def _clean_json_string(self, json_str: str) -> str:
        match = re.search(r'```json\n(.*?)\n```', json_str, re.DOTALL)
        if match:
            return match.group(1).strip()
        return json_str.strip()