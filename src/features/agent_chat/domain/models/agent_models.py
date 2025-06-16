from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
import uuid

class Author(Enum):
    USER = "user"
    AGENT = "agent"

class ModelProvider(Enum):
    OPENAI = "GPT-4o"
    GEMINI = "gemini-2.5-pro-preview-06-05"

class ChatMessage(BaseModel):
    author: Author
    content: str

class PromptStep(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    prompt_template: str
    is_active: bool = True
    order: int

class AgentTask(BaseModel):
    conversation: List[ChatMessage]
    prompt_steps: List[PromptStep]
    model_provider: ModelProvider = ModelProvider.OPENAI
    commit_header: Optional[str] = None

class ExecutionProgress(BaseModel):
    current_step: int = 0
    total_steps: int = 0
    message: str = "Idle"
    is_running: bool = False
