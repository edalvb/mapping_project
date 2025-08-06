"""
Script de prueba para verificar la funcionalidad de expansión/contracción
en DirectorySelectionWidget
"""

import flet as ft
import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from features.project_mapper.presentation.widgets.directory_selection_widget import DirectorySelectionWidget
from features.project_mapper.domain.models.directory_node_model import DirectoryNode


def create_test_tree():
    """Crear un árbol de directorios de prueba"""
    # Crear estructura de directorios de prueba
    root = DirectoryNode(
        name="test_project",
        path="c:/test_project",
        is_directory=True,
        children=[]
    )
    
    # Agregar una carpeta con archivos
    src_folder = DirectoryNode(
        name="src",
        path="c:/test_project/src",
        is_directory=True,
        children=[]
    )
    
    # Archivos en src
    main_file = DirectoryNode(
        name="main.py",
        path="c:/test_project/src/main.py",
        is_directory=False,
        children=[]
    )
    
    utils_file = DirectoryNode(
        name="utils.py",
        path="c:/test_project/src/utils.py",
        is_directory=False,
        children=[]
    )
    
    # Subcarpeta con archivos
    models_folder = DirectoryNode(
        name="models",
        path="c:/test_project/src/models",
        is_directory=True,
        children=[]
    )
    
    user_model = DirectoryNode(
        name="user.py",
        path="c:/test_project/src/models/user.py",
        is_directory=False,
        children=[]
    )
    
    product_model = DirectoryNode(
        name="product.py",
        path="c:/test_project/src/models/product.py",
        is_directory=False,
        children=[]
    )
    
    # Construir el árbol
    models_folder.children = [user_model, product_model]
    src_folder.children = [main_file, utils_file, models_folder]
    
    # Agregar archivo en raíz
    readme_file = DirectoryNode(
        name="README.md",
        path="c:/test_project/README.md",
        is_directory=False,
        children=[]
    )
    
    root.children = [src_folder, readme_file]
    
    return root


def test_expansion_ui(page: ft.Page):
    """Función principal de la app de prueba"""
    page.title = "Prueba de Expansión/Contracción"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 800
    page.window.height = 600
    
    # Crear el árbol de prueba
    test_tree = create_test_tree()
    
    # Estado de selección simulado
    selected_paths = set()
    
    def on_selection_change(paths):
        """Callback cuando cambia la selección"""
        selected_paths.clear()
        selected_paths.update(paths)
        print(f"Selección actualizada: {paths}")
    
    # Crear el widget de selección de directorios
    directory_widget = DirectorySelectionWidget(
        root_node=test_tree,
        selected_paths=selected_paths,
        on_selection_change=on_selection_change,
        is_busy=False
    )
    
    # Información de estado
    info_text = ft.Text(
        "Prueba los botones de flecha para expandir/contraer las carpetas.\n"
        "Las casillas de verificación permiten seleccionar archivos y carpetas.",
        size=14,
        color=ft.Colors.GREY_700
    )
    
    # Layout principal
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("Prueba de Expansión/Contracción", size=20, weight=ft.FontWeight.BOLD),
                info_text,
                ft.Divider(),
                ft.Container(
                    content=directory_widget,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    padding=10,
                    height=400,
                    width=600
                )
            ], spacing=10),
            padding=20
        )
    )


if __name__ == "__main__":
    print("Iniciando prueba de expansión/contracción...")
    ft.app(target=test_expansion_ui)
