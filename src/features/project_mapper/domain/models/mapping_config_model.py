from pydantic import BaseModel
from typing import Set

class MappingConfig(BaseModel):
    project_dir: str
    selected_dirs: Set[str]
    include_extensions: Set[str]
    exclude_patterns: Set[str]
    output_file: str
