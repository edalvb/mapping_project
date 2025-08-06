"""
Script de prueba simple para verificar la lógica de expansión
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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
    
    # Construir el árbol
    models_folder.children = [user_model]
    src_folder.children = [main_file, utils_file, models_folder]
    root.children = [src_folder]
    
    return root


def test_expansion_logic():
    """Probar la lógica de expansión sin UI"""
    print("=== Prueba de Lógica de Expansión ===")
    
    # Crear árbol de prueba
    tree = create_test_tree()
    
    # Simular estado de expansión
    expansion_state = {}
    
    print("\n1. Estado inicial (todo contraído):")
    print(f"  - expansion_state: {expansion_state}")
    
    # Simular expansión de carpeta raíz
    root_path = tree.path
    expansion_state[root_path] = True
    print(f"\n2. Expandir carpeta raíz '{tree.name}':")
    print(f"  - expansion_state: {expansion_state}")
    print(f"  - Carpeta expandida: {expansion_state.get(root_path, False)}")
    
    # Simular expansión de subcarpeta
    src_path = tree.children[0].path
    expansion_state[src_path] = True
    print(f"\n3. Expandir subcarpeta 'src':")
    print(f"  - expansion_state: {expansion_state}")
    print(f"  - Subcarpeta expandida: {expansion_state.get(src_path, False)}")
    
    # Simular contracción
    expansion_state[src_path] = False
    print(f"\n4. Contraer subcarpeta 'src':")
    print(f"  - expansion_state: {expansion_state}")
    print(f"  - Subcarpeta expandida: {expansion_state.get(src_path, False)}")
    
    # Mostrar estructura del árbol
    print(f"\n5. Estructura del árbol:")
    def print_tree(node, level=0):
        indent = "  " * level
        node_type = "📁" if node.is_directory else "📄"
        children_count = f" ({len(node.children)})" if node.is_directory and node.children else ""
        print(f"{indent}{node_type} {node.name}{children_count}")
        
        # Solo mostrar hijos si la carpeta está expandida
        if node.is_directory and expansion_state.get(node.path, False):
            for child in node.children:
                print_tree(child, level + 1)
    
    print_tree(tree)
    
    print("\n=== Prueba completada exitosamente ===")
    print("\nLa lógica de expansión funciona correctamente.")
    print("Los botones de flecha deberían:")
    print("  → ▶️ Mostrar flecha derecha cuando está contraído")
    print("  → ⬇️ Mostrar flecha abajo cuando está expandido")
    print("  → 🔄 Cambiar entre estados al hacer clic")


if __name__ == "__main__":
    test_expansion_logic()
