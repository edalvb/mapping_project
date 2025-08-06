"""
Prueba correcta que simula el comportamiento real del controlador
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
    from features.project_mapper.domain.models.mapping_config_model import MappingConfig
    
    print("✅ PRUEBA CORRECTA CON SIMULACIÓN REAL DEL CONTROLADOR")
    
    # Crear directorio de prueba
    test_dir = Path("test_real_behavior")
    test_dir.mkdir(exist_ok=True)
    
    # Crear estructura
    (test_dir / "apps").mkdir(exist_ok=True)
    (test_dir / "apps" / "expo").mkdir(exist_ok=True)
    
    (test_dir / "apps" / "main.py").write_text("# Main")
    (test_dir / "apps" / "expo" / ".gitignore").write_text("# Gitignore")
    (test_dir / "apps" / "expo" / "app.js").write_text("// App")
    
    print(f"📁 Estructura creada:")
    print(f"   apps/")
    print(f"   ├── main.py")
    print(f"   └── expo/")
    print(f"       ├── .gitignore")
    print(f"       └── app.js")
    
    # CASO 1: Usuario selecciona directorio "apps" (simulando controlador real)
    print(f"\n🧪 CASO 1: Usuario selecciona directorio 'apps'")
    print(f"   (El controlador agrega automáticamente todos los archivos)")
    
    # Simular lo que hace el controlador: agregar todos los archivos del directorio
    selected_paths_caso1 = {
        "apps",                    # Directorio seleccionado
        "apps/main.py",           # Archivo agregado automáticamente
        "apps/expo",              # Subdirectorio agregado automáticamente  
        "apps/expo/.gitignore",   # Archivo agregado automáticamente
        "apps/expo/app.js"        # Archivo agregado automáticamente
    }
    
    config1 = MappingConfig(
        project_dir=str(test_dir),
        selected_paths=selected_paths_caso1,
        include_extensions={".py", ".js", ".gitignore"},
        exclude_patterns=set(),
        output_file="output/test1.md"
    )
    
    repo = FilesystemProjectMapperRepository()
    files1 = repo._get_files_to_process(config1)
    
    print(f"✅ Selected paths: {selected_paths_caso1}")
    print(f"📄 Archivos procesados: {len(files1)}")
    for f in files1:
        print(f"   📄 {f.relative_to(test_dir)}")
    
    # CASO 2: Usuario deselecciona archivo específico "apps/expo/.gitignore"
    print(f"\n🧪 CASO 2: Usuario deselecciona 'apps/expo/.gitignore'")
    print(f"   (El controlador quita solo ese archivo de selected_paths)")
    
    # Simular deselección: quitar solo el archivo específico
    selected_paths_caso2 = selected_paths_caso1.copy()
    selected_paths_caso2.discard("apps/expo/.gitignore")
    
    config2 = MappingConfig(
        project_dir=str(test_dir),
        selected_paths=selected_paths_caso2,
        include_extensions={".py", ".js", ".gitignore"},
        exclude_patterns=set(),
        output_file="output/test2.md"
    )
    
    files2 = repo._get_files_to_process(config2)
    
    print(f"✅ Selected paths: {selected_paths_caso2}")
    print(f"📄 Archivos procesados: {len(files2)}")
    for f in files2:
        print(f"   📄 {f.relative_to(test_dir)}")
    
    # Verificaciones
    gitignore_in_case1 = any(".gitignore" in str(f) for f in files1)
    gitignore_in_case2 = any(".gitignore" in str(f) for f in files2)
    main_py_in_both = any("main.py" in str(f) for f in files1) and any("main.py" in str(f) for f in files2)
    app_js_in_both = any("app.js" in str(f) for f in files1) and any("app.js" in str(f) for f in files2)
    
    print(f"\n📋 VERIFICACIONES:")
    print(f"✅ Caso 1 - .gitignore incluido: {'SÍ' if gitignore_in_case1 else 'NO'}")
    print(f"✅ Caso 2 - .gitignore incluido: {'SÍ' if gitignore_in_case2 else 'NO'}")
    print(f"✅ main.py en ambos casos: {'SÍ' if main_py_in_both else 'NO'}")
    print(f"✅ app.js en ambos casos: {'SÍ' if app_js_in_both else 'NO'}")
    
    caso1_correcto = gitignore_in_case1 and main_py_in_both and app_js_in_both
    caso2_correcto = not gitignore_in_case2 and main_py_in_both and app_js_in_both
    
    print(f"\n🎯 RESULTADOS:")
    print(f"✅ Caso 1 (directorio seleccionado): {'CORRECTO' if caso1_correcto else 'INCORRECTO'}")
    print(f"✅ Caso 2 (archivo deseleccionado): {'CORRECTO' if caso2_correcto else 'INCORRECTO'}")
    
    if caso1_correcto and caso2_correcto:
        print(f"🎉 ¡CORRECCIÓN EXITOSA! El problema de archivos deseleccionados está resuelto.")
    else:
        print(f"❌ Aún hay problemas en la lógica.")
    
    # Limpiar
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    # Limpiar en caso de error
    import shutil
    if 'test_dir' in locals():
        shutil.rmtree(test_dir, ignore_errors=True)
    sys.exit(1)
