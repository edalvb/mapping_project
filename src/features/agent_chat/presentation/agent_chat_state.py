from typing import List, Optional

from pydantic import BaseModel, Field

from ..domain.models.agent_models import (
    ChatMessage,
    ExecutionProgress,
    ModelProvider,
    PromptStep,
)


class AgentChatState(BaseModel):
    conversation: List[ChatMessage] = Field(default_factory=list)
    prompt_steps: List[PromptStep] = Field(default_factory=list)
    progress: ExecutionProgress = Field(default_factory=ExecutionProgress)
    commit_header: Optional[str] = None
    project_directory: Optional[str] = None
    model_provider: ModelProvider = ModelProvider.GEMINI
