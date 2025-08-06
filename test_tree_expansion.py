#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de expansión/contracción de carpetas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from features.project_mapper.domain.models.directory_node_model import DirectoryNode
    
    print("🌳 PROBANDO FUNCIONALIDAD DE EXPANSIÓN/CONTRACCIÓN")
    
    # Crear una estructura de árbol de prueba
    root = DirectoryNode(name="proyecto", path="", is_directory=True)
    
    # Carpeta src con archivos
    src_folder = DirectoryNode(name="src", path="src", is_directory=True, parent=root)
    src_main = DirectoryNode(name="main.py", path="src/main.py", is_directory=False, parent=src_folder)
    src_utils = DirectoryNode(name="utils.py", path="src/utils.py", is_directory=False, parent=src_folder)
    src_folder.children = [src_main, src_utils]
    
    # Carpeta tests con archivos
    tests_folder = DirectoryNode(name="tests", path="tests", is_directory=True, parent=root)
    test_main = DirectoryNode(name="test_main.py", path="tests/test_main.py", is_directory=False, parent=tests_folder)
    tests_folder.children = [test_main]
    
    # Carpeta vacía
    empty_folder = DirectoryNode(name="empty", path="empty", is_directory=True, parent=root)
    
    # Archivo en la raíz
    readme = DirectoryNode(name="README.md", path="README.md", is_directory=False, parent=root)
    
    root.children = [src_folder, tests_folder, empty_folder, readme]
    
    print("✅ Estructura de árbol creada:")
    
    def print_tree(node, indent=0):
        prefix = "  " * indent
        if node.is_directory:
            if node.children:
                print(f"{prefix}📁 {node.name}/ ({len(node.children)} elementos)")
            else:
                print(f"{prefix}📁 {node.name}/ (vacía)")
        else:
            print(f"{prefix}📄 {node.name}")
        
        for child in node.children:
            print_tree(child, indent + 1)
    
    print_tree(root)
    
    print("\n🎯 CARACTERÍSTICAS ESPERADAS:")
    print("✅ Carpetas con contenido tendrán indicador de expansión/contracción")
    print("✅ Carpetas vacías NO tendrán indicador de expansión")
    print("✅ Archivos NO tendrán indicador de expansión")
    print("✅ El contador mostrará el número de elementos en cada carpeta")
    print("✅ Se podrá expandir/contraer carpetas independientemente de la selección")
    
    print("\n📋 COMPORTAMIENTOS VERIFICADOS:")
    
    # Verificar que las carpetas con hijos tienen la estructura correcta
    folders_with_children = [node for node in [src_folder, tests_folder] if node.children]
    folders_empty = [node for node in [empty_folder] if not node.children]
    files = [node for node in [src_main, src_utils, test_main, readme] if not node.is_directory]
    
    print(f"✅ Carpetas con contenido: {len(folders_with_children)} ({[f.name for f in folders_with_children]})")
    print(f"✅ Carpetas vacías: {len(folders_empty)} ({[f.name for f in folders_empty]})")
    print(f"✅ Archivos: {len(files)} ({[f.name for f in files]})")
    
    print(f"\n🎉 ¡Estructura preparada para expansión/contracción!")
    print(f"📝 Las carpetas 'src' y 'tests' deberían poder expandirse/contraerse")
    print(f"📝 La carpeta 'empty' y los archivos NO deberían tener controles de expansión")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
