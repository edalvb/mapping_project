from pydantic import BaseModel, Field
from typing import Optional, Set

class ProjectMapperState(BaseModel):
    project_dir_path: Optional[str] = None
    include_extensions: Set[str] = Field(default_factory=set)
    exclude_patterns: Set[str] = Field(default_factory=set)
    new_include_extension: str = ""
    new_exclude_pattern: str = ""
    is_loading: bool = False
    status_text: str = ""