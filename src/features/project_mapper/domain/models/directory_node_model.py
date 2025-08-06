from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class DirectoryNode(BaseModel):
    name: str
    path: str
    is_directory: bool = True
    children: List[DirectoryNode] = Field(default_factory=list)
    parent: Optional[DirectoryNode] = None

    class Config:
        arbitrary_types_allowed = True

DirectoryNode.model_rebuild()