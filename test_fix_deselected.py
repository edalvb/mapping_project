"""
Script de prueba para verificar la corrección del problema de archivos deseleccionados
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
    from features.project_mapper.domain.models.mapping_config_model import MappingConfig
    
    print("🧪 PROBANDO CORRECCIÓN DE ARCHIVOS DESELECCIONADOS")
    
    # Crear directorio de prueba temporal
    test_dir = Path("test_project_temp")
    test_dir.mkdir(exist_ok=True)
    
    # Crear estructura de prueba
    (test_dir / "apps").mkdir(exist_ok=True)
    (test_dir / "apps" / "expo").mkdir(exist_ok=True)
    
    # Crear archivos de prueba
    (test_dir / "apps" / "expo" / ".gitignore").write_text("# Test gitignore")
    (test_dir / "apps" / "expo" / "app.js").write_text("// Test app")
    (test_dir / "apps" / "main.py").write_text("# Test main")
    (test_dir / "README.md").write_text("# Test readme")
    
    print(f"📁 Estructura de prueba creada en: {test_dir}")
    
    # CASO 1: Directorio seleccionado, archivo específico deseleccionado
    print(f"\n🧪 CASO 1: Directorio 'apps' seleccionado, 'apps/expo/.gitignore' deseleccionado")
    
    selected_paths_case1 = {
        "apps",  # Directorio seleccionado
        "apps/main.py",  # Archivo específico seleccionado
        "apps/expo/app.js",  # Otro archivo específico seleccionado
        # "apps/expo/.gitignore" NO está aquí (deseleccionado)
    }
    
    config_case1 = MappingConfig(
        project_dir=str(test_dir),
        selected_paths=selected_paths_case1,
        include_extensions={".py", ".js", ".gitignore", ".md"},
        exclude_patterns=set(),
        output_file="output/test.md"
    )
    
    repo = FilesystemProjectMapperRepository()
    files_case1 = repo._get_files_to_process(config_case1)
    
    print(f"✅ Rutas seleccionadas: {selected_paths_case1}")
    print(f"📄 Archivos procesados: {len(files_case1)}")
    
    gitignore_included_case1 = any(".gitignore" in str(f) for f in files_case1)
    main_py_included_case1 = any("main.py" in str(f) for f in files_case1)
    app_js_included_case1 = any("app.js" in str(f) for f in files_case1)
    
    print(f"   🔍 .gitignore incluido: {'❌ SÍ (PROBLEMA)' if gitignore_included_case1 else '✅ NO (CORRECTO)'}")
    print(f"   🔍 main.py incluido: {'✅ SÍ (CORRECTO)' if main_py_included_case1 else '❌ NO (PROBLEMA)'}")
    print(f"   🔍 app.js incluido: {'✅ SÍ (CORRECTO)' if app_js_included_case1 else '❌ NO (PROBLEMA)'}")
    
    # CASO 2: Solo directorio seleccionado, sin archivos específicos
    print(f"\n🧪 CASO 2: Solo directorio 'apps' seleccionado (sin archivos específicos)")
    
    selected_paths_case2 = {
        "apps",  # Solo directorio seleccionado
    }
    
    config_case2 = MappingConfig(
        project_dir=str(test_dir),
        selected_paths=selected_paths_case2,
        include_extensions={".py", ".js", ".gitignore", ".md"},
        exclude_patterns=set(),
        output_file="output/test.md"
    )
    
    files_case2 = repo._get_files_to_process(config_case2)
    
    print(f"✅ Rutas seleccionadas: {selected_paths_case2}")
    print(f"📄 Archivos procesados: {len(files_case2)}")
    
    gitignore_included_case2 = any(".gitignore" in str(f) for f in files_case2)
    main_py_included_case2 = any("main.py" in str(f) for f in files_case2)
    app_js_included_case2 = any("app.js" in str(f) for f in files_case2)
    
    print(f"   🔍 .gitignore incluido: {'✅ SÍ (CORRECTO)' if gitignore_included_case2 else '❌ NO (PROBLEMA)'}")
    print(f"   🔍 main.py incluido: {'✅ SÍ (CORRECTO)' if main_py_included_case2 else '❌ NO (PROBLEMA)'}")
    print(f"   🔍 app.js incluido: {'✅ SÍ (CORRECTO)' if app_js_included_case2 else '❌ NO (PROBLEMA)'}")
    
    print(f"\n📋 ANÁLISIS DE RESULTADOS:")
    if not gitignore_included_case1:
        print(f"✅ CASO 1 CORRECTO: Archivo deseleccionado no se incluye")
    else:
        print(f"❌ CASO 1 INCORRECTO: Archivo deseleccionado aún se incluye")
    
    if gitignore_included_case2:
        print(f"✅ CASO 2 CORRECTO: Cuando solo directorio seleccionado, todos los archivos se incluyen")
    else:
        print(f"❌ CASO 2 INCORRECTO: Archivos del directorio no se incluyen")
    
    # Limpiar archivos de prueba
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    print(f"\n🧹 Archivos de prueba limpiados")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    # Limpiar en caso de error
    import shutil
    if 'test_dir' in locals():
        shutil.rmtree(test_dir, ignore_errors=True)
    sys.exit(1)
