from pydantic import BaseModel, Field
from typing import Optional, Set
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
    selected_dirs: Set[str] = Field(default_factory=set)

    class Config:
        arbitrary_types_allowed = True