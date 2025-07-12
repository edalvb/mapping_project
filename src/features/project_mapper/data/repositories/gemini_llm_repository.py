from typing import List
import os
import json
import base64

from google import genai
from google.genai import types

from src.features.project_mapper.domain.models.llm_config_model import LLMConfig
from src.features.project_mapper.domain.models.llm_response_model import LLMSuggestionResponse
from src.features.project_mapper.domain.repositories.i_llm_repository import I_LLMRepository

class GeminiLLMRepository(I_LLMRepository):
    _client: genai.Client = None

    def change_api_key(self, api_key: str):
        print("Configurando la clave de API de Gemini...")

        if not api_key or not api_key.strip():
            raise ValueError("La clave de API de Gemini no fue proporcionada.")

        try:
            self._client = genai.Client(api_key=api_key)
        except Exception as e:
            raise RuntimeError(f"No se pudo conectar a la API de Gemini: {e}") from e

    def get_models(self, api_key: str) -> List[str]:
        if not api_key or not api_key.strip():
            raise ValueError("La clave de API de Gemini no fue proporcionada.")
        try:
            self.change_api_key(api_key)
            return [model.name for model in self._client.models.list()]
        except Exception as e:
            raise RuntimeError(f"No se pudo conectar a la API de Gemini: {e}") from e

    def get_available_models(self, api_key: str) -> List[str]:
        if not api_key or not api_key.strip():
            raise ValueError("La clave de API de Gemini no fue proporcionada.")

        try:
            self.change_api_key(api_key)
            return self.get_models(api_key)
        except Exception as e:
            raise RuntimeError(f"No se pudo conectar a la API de Gemini: {e}") from e

    def get_intelligent_selection(
        self, config: LLMConfig, project_map_content: str
    ) -> LLMSuggestionResponse:
        if not config.api_key or not config.api_key.strip():
            raise ValueError("La clave de API de Gemini no está configurada en la configuración del LLM.")

        self.change_api_key(config.api_key)

        try:
            print("Proyecto mapeado recibido correctamente.")
            print(f"Contenido del proyecto mapeado: {project_map_content[:100]}...")  # Mostrar solo los primeros 100 caracteres

            prompt_parts = [
                types.Part.from_bytes(
                    mime_type="text/markdown",
                    data=project_map_content.encode("utf-8"),
                ),
                types.Part(text=f"Mi objetivo es: {config.objective}"),
            ]

            print("Partes del prompt creadas correctamente.")
        except Exception as e:
            raise ValueError(f"Error al crear las partes del prompt: {e}")

        try:
            response_schema = types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'suggested_paths': types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
                    'reasoning': types.Schema(type=types.Type.STRING)
                },
                required=['suggested_paths', 'reasoning']
            )

            print("Esquema de respuesta creado correctamente.")
        except Exception as e:
            raise ValueError(f"Error al crear el esquema de respuesta: {e}")

        try:
            generate_content_config = types.GenerateContentConfig(
                # thinking_config=types.ThinkingConfig(
                #     thinking_budget=32768,
                # ),
                # media_resolution=types.MediaResolution.MEDIA_RESOLUTION_MEDIUM,
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=1.0,
                system_instruction=[
                    types.Part.from_text(text=config.system_instruction),
                ],
            )

            print("Configuración de generación de contenido creada correctamente.")
        except Exception as e:
            raise ValueError(f"Error al crear la configuración de generación de contenido: {e}")

        try:
            model = self._client.models.generate_content(
                model=config.model_name,
                config=generate_content_config,
                contents=[
                    types.Content(
                        role="user",
                        parts=prompt_parts
                    ),
                ]
            )

            print("Solicitud de generación de contenido enviada correctamente.")
        except Exception as e:
            raise RuntimeError(f"No se pudo generar el contenido con el modelo {config.model_name}: {e}") from e

        response = model
        
        try:
            response_data = json.loads(response.text)
            return LLMSuggestionResponse(**response_data)
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"La respuesta del LLM no es un JSON válido: {e}\nRespuesta recibida: {response.text}")