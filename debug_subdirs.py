"""
Script de debug específico para entender por qué fallan los subdirectorios
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
    from features.project_mapper.domain.models.mapping_config_model import MappingConfig
    
    print("🔍 DEBUG ESPECÍFICO DE SUBDIRECTORIOS")
    
    # Crear directorio de prueba temporal
    test_dir = Path("debug_test_temp")
    test_dir.mkdir(exist_ok=True)
    
    # Crear estructura de prueba simple
    (test_dir / "apps").mkdir(exist_ok=True)
    (test_dir / "apps" / "expo").mkdir(exist_ok=True)
    
    # Crear archivos de prueba
    (test_dir / "apps" / "main.py").write_text("# Main file")
    (test_dir / "apps" / "expo" / ".gitignore").write_text("# Gitignore file")
    (test_dir / "apps" / "expo" / "app.js").write_text("// App file")
    
    print(f"📁 Estructura creada:")
    print(f"   test_dir/")
    print(f"   └── apps/")
    print(f"       ├── main.py")
    print(f"       └── expo/")
    print(f"           ├── .gitignore")
    print(f"           └── app.js")
    
    # Caso de debug: solo directorio apps seleccionado
    selected_paths = {"apps"}
    
    config = MappingConfig(
        project_dir=str(test_dir),
        selected_paths=selected_paths,
        include_extensions={".py", ".js", ".gitignore"},
        exclude_patterns=set(),
        output_file="output/debug.md"
    )
    
    print(f"\n🎯 Configuración:")
    print(f"   Selected paths: {selected_paths}")
    print(f"   Project dir: {test_dir}")
    
    # Crear repo con debug
    repo = FilesystemProjectMapperRepository()
    
    # Simular el proceso paso a paso
    project_path = Path(config.project_dir)
    selected_paths_set = config.selected_paths
    
    print(f"\n🔄 Proceso paso a paso:")
    
    # Separar archivos y directorios
    selected_files = set()
    selected_directories = set()
    
    for path in selected_paths_set:
        full_path = project_path / path
        if full_path.is_file():
            selected_files.add(path)
            print(f"   📄 Archivo seleccionado: {path}")
        elif full_path.is_dir():
            selected_directories.add(path)
            print(f"   📁 Directorio seleccionado: {path}")
    
    print(f"\n📂 Directorios seleccionados: {selected_directories}")
    print(f"📄 Archivos seleccionados: {selected_files}")
    
    # Simular os.walk
    print(f"\n🚶 Simulando os.walk:")
    all_files = set()
    
    for root, dirs, files in os.walk(project_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in repo.EXCLUDED_DIRS]
        
        current_path_str = Path(root).relative_to(project_path).as_posix()
        if current_path_str == '.':
            current_path_str = ''
        
        print(f"\n   🗂️ Procesando directorio: '{current_path_str}'")
        print(f"      📁 Subdirectorios: {dirs}")
        print(f"      📄 Archivos: {files}")
        
        # Verificar si está seleccionado
        is_directory_selected = any(
            current_path_str == sel_dir or 
            (sel_dir and current_path_str.startswith(sel_dir + '/'))
            for sel_dir in selected_directories
        )
        
        print(f"      ✅ Directorio seleccionado: {is_directory_selected}")
        
        if is_directory_selected:
            print(f"      🔍 Procesando archivos en directorio seleccionado:")
            for filename in files:
                file_path = Path(root) / filename
                file_path_str = file_path.relative_to(project_path).as_posix()
                
                print(f"         📄 Archivo: {file_path_str}")
                
                # Verificar si está en selected_paths
                in_selected = file_path_str in selected_paths_set
                print(f"            En selected_paths: {in_selected}")
                
                if in_selected:
                    all_files.add(file_path)
                    print(f"            ✅ INCLUIDO (explícitamente seleccionado)")
                else:
                    # Verificar selección granular
                    has_granular = any(
                        p for p in selected_paths_set 
                        if Path(project_path / p).is_file() and 
                        (p.startswith(current_path_str + '/') if current_path_str else '/' not in p)
                    )
                    print(f"            Selección granular en directorio: {has_granular}")
                    
                    if not has_granular:
                        all_files.add(file_path)
                        print(f"            ✅ INCLUIDO (directorio sin selección granular)")
                    else:
                        print(f"            ❌ EXCLUIDO (selección granular activa)")
    
    print(f"\n📋 RESULTADO FINAL:")
    print(f"   Total archivos incluidos: {len(all_files)}")
    for file_path in sorted(all_files):
        print(f"   ✅ {file_path.relative_to(project_path)}")
    
    # Limpiar
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
