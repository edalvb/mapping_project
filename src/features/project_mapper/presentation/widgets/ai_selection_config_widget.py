import flet as ft
from typing import Callable, List, Optional
from src.shared.presentation.theme import CORTEX_AI_PALETTE

class AISelectionConfigWidget(ft.Column):
    def __init__(
        self,
        api_key: str,
        models_loaded: bool,
        available_models: List[str],
        selected_model: Optional[str],
        system_instruction: str,
        objective: str,
        is_ai_selecting: bool,
        ai_status_text: str,
        on_change_api_key: Callable,
        on_verify_api_key: Callable,
        on_change_model: Callable,
        on_change_instruction: Callable,
        on_change_objective: Callable,
    ):
        super().__init__()
        self.spacing = 15
        self.scroll = ft.ScrollMode.ADAPTIVE

        self.controls = [
            ft.Text("Configuración de IA", style=ft.TextThemeStyle.HEADLINE_SMALL),
            ft.TextField(
                label="Clave API de Gemini",
                value=api_key,
                on_change=on_change_api_key,
                password=True,
                can_reveal_password=True,
                hint_text="Introduce tu clave de API",
                disabled=is_ai_selecting,
            ),
            ft.ElevatedButton(
                "Verificar y Cargar Modelos",
                icon=ft.Icons.CLOUD_SYNC,
                on_click=on_verify_api_key,
                disabled=not api_key or is_ai_selecting,
            ),
            ft.Dropdown(
                label="Modelo de Lenguaje",
                options=[
                    ft.dropdown.Option(model_id, text=model_id.replace("models/", ""))
                    for model_id in available_models
                ],
                value=selected_model,
                on_change=on_change_model,
                disabled=not models_loaded or is_ai_selecting,
                hint_text="Verifique la clave para cargar modelos"
            ),
            ft.TextField(
                label="Objetivo del Mapeo",
                value=objective,
                on_change=on_change_objective,
                hint_text="Ej: Quiero refactorizar la gestión de estado.",
                disabled=not models_loaded or is_ai_selecting,
            ),
            ft.TextField(
                label="Instrucción de Sistema (Avanzado)",
                value=system_instruction,
                on_change=on_change_instruction,
                multiline=True,
                min_lines=5,
                max_lines=8,
                disabled=not models_loaded or is_ai_selecting,
            ),
            ft.Row(
                [
                    ft.ProgressRing(width=16, height=16, stroke_width=2),
                    ft.Text(ai_status_text, expand=True, selectable=True),
                ],
                visible=is_ai_selecting,
            ),
        ]