from typing import Dict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from .....core.config import Settings
from ...domain.repositories.i_llm_repository import ILLMRepository


class GeminiRepository(ILLMRepository):
    def __init__(self, settings: Settings, max_retries: int = 5):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("Google API key is not set.")

        self._model = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro-preview-06-05",
            temperature=0.0,
            max_retries=max_retries,
            google_api_key=settings.GOOGLE_API_KEY
        )
        self._parser = StrOutputParser()

    def execute_prompt(self, prompt_template: str, context: Dict[str, str]) -> str:
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self._model | self._parser
        response = chain.invoke(context)
        return response
