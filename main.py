# Main entry point for Flet build
# Self-contained version that imports everything directly

import sys
import os

def get_application_path():
    """Get the path where the application is running from."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

# Add src directory to Python path for imports
app_path = get_application_path()
src_path = os.path.join(app_path, 'src')

# Try multiple possible src locations
possible_src_paths = [
    src_path,
    os.path.join(os.path.dirname(__file__), 'src') if '__file__' in globals() else None,
    os.path.join(os.getcwd(), 'src'),
    'src'
]

# Add all possible paths to sys.path
for path in possible_src_paths:
    if path and os.path.exists(path):
        if path not in sys.path:
            sys.path.insert(0, path)

# Import Flet
import flet as ft

# Now import the application components
try:
    from features.file_creator.data.repositories.filesystem_file_creator_repository import FilesystemFileCreatorRepository
    from features.file_creator.domain.services.file_creator_service import FileCreatorService
    from features.file_creator.presentation.file_creator_state import FileCreatorState
    from features.file_creator.presentation.file_creator_controller import FileCreatorController
    from features.file_creator.presentation.file_creator_view import FileCreatorView

    from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
    from features.project_mapper.data.repositories.gemini_llm_repository import GeminiLLMRepository
    from features.project_mapper.domain.services.project_mapper_service import ProjectMapperService
    from features.project_mapper.presentation.project_mapper_state import ProjectMapperState
    from features.project_mapper.presentation.project_mapper_controller import ProjectMapperController
    from features.project_mapper.presentation.view.project_mapper_view import ProjectMapperView

    from shared.presentation.theme import CORTEX_AI_THEME

    def main(page: ft.Page):
        page.title = "Cortex AI - Utilidad de Desarrollo"
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.window_width = 1200
        page.window_height = 800
        page.theme = CORTEX_AI_THEME
        page.dark_theme = CORTEX_AI_THEME

        main_container = ft.Container(
            width=page.window_width,
            height=page.window_height,
            padding=ft.padding.all(20),
            expand=True,
        )

        # --- INYECCIÓN DE DEPENDENCIAS ---

        # Slice: File Creator
        file_creator_repository = FilesystemFileCreatorRepository()
        file_creator_service = FileCreatorService(file_creator_repository)
        file_creator_state = FileCreatorState()
        file_creator_controller = FileCreatorController(page, file_creator_state, file_creator_service)
        file_creator_view = FileCreatorView(file_creator_controller, file_creator_state)
        file_creator_controller.view = file_creator_view

        # Slice: Project Mapper
        project_mapper_repository = FilesystemProjectMapperRepository()
        gemini_llm_repository = GeminiLLMRepository()
        project_mapper_service = ProjectMapperService(
            mapper_repository=project_mapper_repository,
            llm_repository=gemini_llm_repository
        )
        project_mapper_state = ProjectMapperState()
        project_mapper_controller = ProjectMapperController(page, project_mapper_state, project_mapper_service)
        project_mapper_view = ProjectMapperView(project_mapper_controller, project_mapper_state)
        project_mapper_controller.view = project_mapper_view

        # --- COMPOSICIÓN DE UI ---

        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Crear desde JSON",
                    content=file_creator_view,
                    icon=ft.Icons.SOURCE
                ),
                ft.Tab(
                    text="Mapear Proyecto",
                    content=project_mapper_view,
                    icon=ft.Icons.MAP
                ),
            ],
            expand=True,
        )

        main_container.content = tabs

        page.add(main_container)
        page.update()
        
except ImportError as e:
    print(f"Error importing application modules: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Application path: {app_path}")
    print(f"Python path: {sys.path}")
    
    # Fallback: create a simple error page
    def main(page: ft.Page):
        page.title = "Cortex AI - Error"
        page.add(ft.Text(f"Error: No se pudieron cargar los módulos de la aplicación.\n\nDetalles: {e}"))
    
if __name__ == "__main__":
    ft.app(target=main)
