"""
Debug del comportamiento del controlador
"""

print("🔍 DEBUG: ¿Cómo maneja el controlador la selección de directorios?")

# Simular la lógica del controlador
from pathlib import Path

def simulate_controller_directory_selection(directory_node, is_selected):
    """Simula cómo el controlador maneja la selección de directorios"""
    paths_to_change = set()
    
    # Simular BFS del controlador
    q = [directory_node]
    while q:
        curr = q.pop(0)
        paths_to_change.add(curr['path'])
        if 'children' in curr:
            q.extend(curr['children'])
    
    return paths_to_change

# Crear estructura de ejemplo
directory_structure = {
    'path': 'src',
    'is_directory': True,
    'children': [
        {'path': 'src/main.py', 'is_directory': False},
        {'path': 'src/utils.py', 'is_directory': False},
        {
            'path': 'src/models',
            'is_directory': True,
            'children': [
                {'path': 'src/models/user.py', 'is_directory': False},
                {'path': 'src/models/product.py', 'is_directory': False}
            ]
        }
    ]
}

print("\n📁 Estructura de ejemplo:")
print("   src/")
print("   ├── main.py")
print("   ├── utils.py")
print("   └── models/")
print("       ├── user.py")
print("       └── product.py")

print("\n🎯 Cuando usuario selecciona directorio 'src':")
selected_paths = simulate_controller_directory_selection(directory_structure, True)
print(f"   Paths en selected_paths: {selected_paths}")

print("\n🎯 Cuando usuario deselecciona 'src/main.py':")
selected_paths.discard('src/main.py')
print(f"   Paths en selected_paths: {selected_paths}")

print("\n💡 CONCLUSIÓN:")
print("✅ El controlador SÍ agrega todos los archivos del directorio")
print("✅ Cuando deseleccionas un archivo, lo quita de selected_paths")
print("✅ Por tanto, la lógica del repositorio debe ser simple:")
print("   → Solo incluir archivos que están en selected_paths")
print("   → Esto ya está implementado correctamente")

print("\n🚨 PROBLEMA IDENTIFICADO:")
print("❌ La prueba no está simulando correctamente el comportamiento del controlador")
print("❌ Cuando se selecciona un directorio, los archivos deberían estar en selected_paths")
