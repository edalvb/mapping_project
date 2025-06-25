from pydantic import BaseModel, Field
from typing import Optional

class FileCreatorState(BaseModel):
    base_dir_path: Optional[str] = None
    json_file_path: Optional[str] = None
    is_loading: bool = False
    status_text: str = ""