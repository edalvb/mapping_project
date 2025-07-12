from pydantic import BaseModel
from typing import List

class LLMSuggestionResponse(BaseModel):
    suggested_paths: List[str]
    reasoning: str
