from pydantic import BaseModel, RootModel
from typing import List

class FileContent(BaseModel):
    path: str
    content: str

class FileContentList(RootModel[List[FileContent]]):
    root: List[FileContent]
