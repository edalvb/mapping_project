import flet as ft

from features.file_creator.data.repositories.filesystem_file_creator_repository import FilesystemFileCreatorRepository
from features.file_creator.domain.services.file_creator_service import FileCreatorService
from features.file_creator.presentation.file_creator_state import FileCreatorState
from features.file_creator.presentation.file_creator_controller import FileCreatorController
from features.file_creator.presentation.file_creator_view import FileCreatorView

from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
from features.project_mapper.domain.services.project_mapper_service import ProjectMapperService
from features.project_mapper.presentation.project_mapper_state import ProjectMapperState
from features.project_mapper.presentation.project_mapper_controller import ProjectMapperController
from features.project_mapper.presentation.project_mapper_view import ProjectMapperView

from shared.presentation.theme import CORTEX_AI_THEME

def main(page: ft.Page):
    page.title = "Cortex AI - Utilidad de Desarrollo"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 850
    page.window_height = 700
    page.theme = CORTEX_AI_THEME
    page.dark_theme = CORTEX_AI_THEME

    # --- INYECCIÓN DE DEPENDENCIAS Y COMPOSICIÓN DE UI ---

    # Slice: File Creator
    file_creator_repository = FilesystemFileCreatorRepository()
    file_creator_service = FileCreatorService(file_creator_repository)
    file_creator_state = FileCreatorState()
    file_creator_controller = FileCreatorController(page, file_creator_state, file_creator_service)

    # Slice: Project Mapper
    project_mapper_repository = FilesystemProjectMapperRepository()
    project_mapper_service = ProjectMapperService(project_mapper_repository)
    project_mapper_state = ProjectMapperState()
    project_mapper_controller = ProjectMapperController(page, project_mapper_state, project_mapper_service)

    # Control principal de la UI
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Crear desde JSON",
                content=FileCreatorView(file_creator_controller, file_creator_state),
                icon=ft.Icons.SOURCE
            ),
            ft.Tab(
                text="Mapear Proyecto",
                content=ProjectMapperView(project_mapper_controller, project_mapper_state),
                icon=ft.Icons.MAP
            ),
        ],
        expand=True,
    )

    # Añadir el control principal a la página
    page.add(tabs)
    page.update()

if __name__ == "__main__":
    # Para asegurar que las importaciones funcionen, ejecuta desde la raíz del proyecto:
    # python -m src.main
    ft.app(target=main)