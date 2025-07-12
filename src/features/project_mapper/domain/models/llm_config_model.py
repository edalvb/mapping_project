from pydantic import BaseModel
from typing import Optional

class LLMConfig(BaseModel):
    system_instruction: str
    objective: str
    model_name: str
    api_key: Optional[str] = None
