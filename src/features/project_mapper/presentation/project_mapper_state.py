from pydantic import BaseModel, Field
from typing import Optional, Set, List
from src.features.project_mapper.domain.models.directory_node_model import DirectoryNode

class ProjectMapperState(BaseModel):
    project_dir_path: Optional[str] = None
    output_dir_path: Optional[str] = None
    output_filename: str = ""
    include_extensions: Set[str] = Field(default_factory=set)
    exclude_patterns: Set[str] = Field(default_factory=set)
    new_include_extension: str = ""
    new_exclude_pattern: str = ""
    is_loading: bool = False
    status_text: str = ""
    directory_tree: Optional[DirectoryNode] = None
    selected_paths: Set[str] = Field(default_factory=set)
    right_panel_tab_index: int = 0

    llm_system_instruction: str = (
        "Eres un experto arquitecto de software. Analiza el siguiente mapeo de proyecto. "
        "Basado en el objetivo del usuario, selecciona las carpetas más relevantes para la tarea. "
        "Debes devolver únicamente un objeto JSON con las claves 'suggested_paths' (una lista de strings con las rutas relativas de las carpetas seleccionadas) y 'reasoning' (una breve explicación de tu elección)."
    )
    llm_objective: str = ""
    llm_api_key: str = ""
    llm_models_loaded: bool = False
    available_llm_models: List[str] = Field(default_factory=list)
    selected_llm_model: Optional[str] = None
    is_ai_selecting: bool = False
    ai_status_text: str = ""

    class Config:
        arbitrary_types_allowed = True
