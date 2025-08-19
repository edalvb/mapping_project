"""
Script para debuggear el problema de selección/deselección de carpetas
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
    from features.project_mapper.domain.models.mapping_config_model import MappingConfig
    
    print("🔍 DEBUGGEANDO PROBLEMA DE SELECCIÓN")
    
    # Crear directorio de prueba temporal
    test_dir = Path("test_debug_temp")
    test_dir.mkdir(exist_ok=True)
    
    # Crear estructura simple
    (test_dir / "src").mkdir(exist_ok=True)
    (test_dir / "src" / "features").mkdir(exist_ok=True)
    (test_dir / "src" / "features" / "dashboard").mkdir(exist_ok=True)
    
    # Crear archivos
    (test_dir / "src" / "main.py").write_text("# Main file")
    (test_dir / "src" / "utils.py").write_text("# Utils file")
    (test_dir / "src" / "features" / "__init__.py").write_text("# Init file")
    (test_dir / "src" / "features" / "dashboard" / "component.py").write_text("# Component file")
    (test_dir / "src" / "features" / "dashboard" / "styles.css").write_text("/* Styles */")
    
    print(f"📁 Estructura creada en: {test_dir}")
    print("   src/")
    print("   ├── main.py")
    print("   ├── utils.py")
    print("   └── features/")
    print("       ├── __init__.py")
    print("       └── dashboard/")
    print("           ├── component.py")
    print("           └── styles.css")
    
    repo = FilesystemProjectMapperRepository()
    
    # CASO 1: Solo seleccionar carpeta "src"
    print(f"\n🧪 CASO 1: Solo carpeta 'src' seleccionada")
    config1 = MappingConfig(
        project_dir=str(test_dir),
        selected_paths={"src"},
        include_extensions={".py", ".css"},
        exclude_patterns=set(),
        output_file="output/test1.md"
    )
    
    files1 = repo._get_files_to_process(config1)
    print(f"✅ Selected paths: {config1.selected_paths}")
    print(f"📄 Archivos encontrados: {len(files1)}")
    for f in files1:
        print(f"   📄 {f.relative_to(test_dir)}")
    
    # CASO 2: Simular comportamiento del controlador - expandir la carpeta src
    print(f"\n🧪 CASO 2: Carpeta 'src' expandida (como haría el controlador)")
    # Cuando el usuario selecciona "src", el controlador agrega todos los paths
    expanded_paths = {
        "src",
        "src/main.py",
        "src/utils.py", 
        "src/features",
        "src/features/__init__.py",
        "src/features/dashboard",
        "src/features/dashboard/component.py",
        "src/features/dashboard/styles.css"
    }
    
    config2 = MappingConfig(
        project_dir=str(test_dir),
        selected_paths=expanded_paths,
        include_extensions={".py", ".css"},
        exclude_patterns=set(),
        output_file="output/test2.md"
    )
    
    files2 = repo._get_files_to_process(config2)
    print(f"✅ Selected paths (expandido): {len(config2.selected_paths)} paths")
    print(f"📄 Archivos encontrados: {len(files2)}")
    for f in files2:
        print(f"   📄 {f.relative_to(test_dir)}")
    
    # CASO 3: Usuario deselecciona "src/features/dashboard"
    print(f"\n🧪 CASO 3: Usuario deselecciona 'src/features/dashboard'")
    # El controlador quita toda la carpeta dashboard
    deselected_paths = expanded_paths.copy()
    deselected_paths.discard("src/features/dashboard")
    deselected_paths.discard("src/features/dashboard/component.py")
    deselected_paths.discard("src/features/dashboard/styles.css")
    
    config3 = MappingConfig(
        project_dir=str(test_dir),
        selected_paths=deselected_paths,
        include_extensions={".py", ".css"},
        exclude_patterns=set(),
        output_file="output/test3.md"
    )
    
    files3 = repo._get_files_to_process(config3)
    print(f"❌ Paths deseleccionados: src/features/dashboard/* (3 paths removed)")
    print(f"✅ Selected paths restantes: {len(config3.selected_paths)} paths")
    print(f"📄 Archivos encontrados: {len(files3)}")
    for f in files3:
        print(f"   📄 {f.relative_to(test_dir)}")
    
    # Verificar si funciona correctamente
    dashboard_files_excluded = not any("dashboard" in str(f) for f in files3)
    main_files_included = any("main.py" in str(f) for f in files3)
    
    print(f"\n📋 VERIFICACIÓN:")
    print(f"✅ Archivos de dashboard excluidos: {'SÍ' if dashboard_files_excluded else 'NO'}")
    print(f"✅ main.py incluido: {'SÍ' if main_files_included else 'NO'}")
    
    if dashboard_files_excluded and main_files_included:
        print(f"🎉 ¡FUNCIONA CORRECTAMENTE!")
    else:
        print(f"🚨 HAY UN PROBLEMA")
    
    # Limpiar
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
