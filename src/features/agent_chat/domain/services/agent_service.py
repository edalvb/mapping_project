import json
from typing import Callable, Dict, List

from ...data.dto.code_generation_dto import FileContentList
from ..models.agent_models import AgentTask, ExecutionProgress, ModelProvider
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

        list_files_step = next((s for s in active_steps if "lista" in s.name.lower()), None)
        code_gen_step = next((s for s in active_steps if "codifica" in s.name.lower()), None)
        commit_step = next((s for s in active_steps if "commit" in s.name.lower()), None)

        file_list_json_str = ""
        for step in [s for s in active_steps if s not in [code_gen_step, commit_step]]:
            progress.message = f"Executing: {step.name}"
            progress_callback(progress)
            result = llm_repo.execute_prompt(step.prompt_template, context)
            context[f"{step.name.lower().replace(' ', '_')}_result"] = result
            if step == list_files_step:
                file_list_json_str = result

        if code_gen_step and file_list_json_str:
            self._process_code_generation(
                code_gen_step.prompt_template, context, file_list_json_str,
                progress, progress_callback, project_dir, llm_repo
            )

        if commit_step:
            progress.message = f"Executing: {commit_step.name}"
            progress_callback(progress)
            llm_repo.execute_prompt(commit_step.prompt_template, context)

        progress.message = "Task completed successfully."

    def _process_code_generation(
        self, template: str, context: Dict[str, str], file_list_json: str,
        progress: ExecutionProgress, progress_callback: Callable[[ExecutionProgress], None],
        project_dir: str, llm_repo: ILLMRepository
    ):
        work_queue = self._parse_file_list(file_list_json)
        batches = [work_queue[i:i + 2] for i in range(0, len(work_queue), 2)]

        for i, batch in enumerate(batches):
            progress.message = f"Generating code for batch {i+1}/{len(batches)}"
            progress_callback(progress)

            batch_context = context.copy()
            batch_context["file_list"] = "\n".join([f"- {item['path']}" for item in batch])

            code_json_str = llm_repo.execute_prompt(template, batch_context)
            file_contents = FileContentList.model_validate_json(code_json_str)
            
            for file_content in file_contents.root:
                full_path = f"{project_dir}/{file_content.path}"
                self._fs_repo.write_file(full_path, file_content.content)

            context["project_map"] = self._mapper_repo.map_project_to_string(project_dir, [], [])
            progress_callback(progress)

    def _initialize_context(self, task: AgentTask, project_dir: str) -> Dict[str, str]:
        if not self._fs_repo.is_directory(project_dir):
            raise ValueError(f"Project directory not found: {project_dir}")

        project_map = self._mapper_repo.map_project_to_string(project_dir, [], [])
        conversation_history = "\n".join([f"{msg.author.value}: {msg.content}" for msg in task.conversation])
        
        return {
            "project_map": project_map,
            "conversation": conversation_history,
            "commit_header": task.commit_header or ""
        }

    def _parse_file_list(self, json_str: str) -> List[Dict[str, str]]:
        try:
            data = json.loads(json_str)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []
