"""
Script para reproducir el problema de archivos deseleccionados que aún se cuentan
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
    from features.project_mapper.domain.models.mapping_config_model import MappingConfig
    
    print("🐛 REPRODUCIENDO PROBLEMA DE ARCHIVOS DESELECCIONADOS")
    
    # Simular configuración problemática
    project_dir = "."  # Directorio actual
    
    # Caso problemático: directorio seleccionado, archivo específico deseleccionado
    selected_paths = {
        "src",  # Directorio seleccionado
        # "apps/expo/.gitignore" NO está en selected_paths (está deseleccionado)
    }
    
    config = MappingConfig(
        project_dir=project_dir,
        selected_paths=selected_paths,
        include_extensions={".py", ".md", ".txt", ".gitignore"},
        exclude_patterns=set(),
        output_file="output/test_output.md"
    )
    
    repo = FilesystemProjectMapperRepository()
    
    print(f"📁 Directorio del proyecto: {project_dir}")
    print(f"✅ Rutas seleccionadas: {selected_paths}")
    print(f"❌ Archivo específico deseleccionado: apps/expo/.gitignore")
    print(f"🎯 Extensiones incluidas: {config.include_extensions}")
    
    print(f"\n📋 ANALIZANDO LÓGICA ACTUAL:")
    
    files_to_process = repo._get_files_to_process(config)
    
    print(f"📄 Total de archivos a procesar: {len(files_to_process)}")
    
    # Buscar si el archivo problemático está incluido
    problematic_file = None
    for file_path in files_to_process:
        if ".gitignore" in str(file_path) and "expo" in str(file_path):
            problematic_file = file_path
            break
    
    if problematic_file:
        print(f"🚨 PROBLEMA ENCONTRADO:")
        print(f"   ❌ El archivo {problematic_file} está siendo incluido")
        print(f"   ❌ Pero NO está en selected_paths")
        print(f"   ❌ Debería estar excluido")
    else:
        print(f"✅ El archivo problemático NO está incluido (comportamiento correcto)")
    
    print(f"\n🔍 ARCHIVOS QUE CONTIENEN '.gitignore':")
    gitignore_files = [f for f in files_to_process if ".gitignore" in str(f)]
    for i, file_path in enumerate(gitignore_files[:5]):  # Mostrar máximo 5
        print(f"   {i+1}. {file_path}")
    
    if len(gitignore_files) > 5:
        print(f"   ... y {len(gitignore_files) - 5} más")
    
    print(f"\n🧩 EXPLICACIÓN DEL PROBLEMA:")
    print(f"1. Usuario selecciona carpeta 'src' ✅")
    print(f"2. Esto incluye TODOS los archivos dentro de 'src' automáticamente")
    print(f"3. Usuario deselecciona 'apps/expo/.gitignore' específicamente ❌")
    print(f"4. PERO la lógica actual no verifica deselecciones individuales")
    print(f"5. El archivo sigue siendo incluido porque su carpeta padre está seleccionada")
    
    print(f"\n💡 SOLUCIÓN NECESARIA:")
    print(f"✅ Verificar selected_paths para archivos individuales")
    print(f"✅ Si un archivo específico NO está en selected_paths, excluirlo")
    print(f"✅ Incluso si su carpeta padre está seleccionada")
    print(f"✅ Dar prioridad a la selección granular sobre la selección de carpeta")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
