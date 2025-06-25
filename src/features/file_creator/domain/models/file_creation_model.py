from pydantic import BaseModel

class FileCreationItem(BaseModel):
    path: str
    content: str