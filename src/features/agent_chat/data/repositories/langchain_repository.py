from typing import Dict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .....core.config import Settings
from ...domain.repositories.i_llm_repository import ILLMRepository


class LangchainRepository(ILLMRepository):
    def __init__(self, settings: Settings, max_retries: int = 5):
        self._model = ChatOpenAI(
            model="gpt-4o",
            temperature=0.0,
            timeout=120,
        ).with_retry(stop_after_attempt=max_retries)
        self._parser = StrOutputParser()

    def execute_prompt(self, prompt_template: str, context: Dict[str, str]) -> str:
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self._model | self._parser
        response = chain.invoke(context)
        return response
