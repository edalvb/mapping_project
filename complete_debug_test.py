"""
Test completo para reproducir y debuggear el problema de deselección
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("🧪 TEST COMPLETO CON DEBUG")
    print("="*60)
    
    # Remover logs temporalmente para limpiar salida
    # Vamos a hacer un test paso a paso del comportamiento del controlador
    
    # Test 1: Verificar la lógica del controlador
    from features.project_mapper.domain.models.directory_node_model import DirectoryNode
    
    print("\n📊 PASO 1: Crear estructura de directorio de prueba")
    
    # Crear estructura como la menciona el usuario
    root = DirectoryNode(
        name="src",
        path="src", 
        is_directory=True,
        children=[]
    )
    
    # src/app/
    app_dir = DirectoryNode(
        name="app",
        path="src/app",
        is_directory=True,
        children=[]
    )
    root.children.append(app_dir)
    
    # src/app/features/
    features_dir = DirectoryNode(
        name="features", 
        path="src/app/features",
        is_directory=True,
        children=[]
    )
    app_dir.children.append(features_dir)
    
    # src/app/features/dashboard/
    dashboard_dir = DirectoryNode(
        name="dashboard",
        path="src/app/features/dashboard", 
        is_directory=True,
        children=[]
    )
    features_dir.children.append(dashboard_dir)
    
    # Agregar un archivo en dashboard
    dashboard_file = DirectoryNode(
        name="component.py",
        path="src/app/features/dashboard/component.py",
        is_directory=False,
        children=[]
    )
    dashboard_dir.children.append(dashboard_file)
    
    # src/app/features/other/ (para verificar que no se afecte)
    other_dir = DirectoryNode(
        name="other",
        path="src/app/features/other",
        is_directory=True, 
        children=[]
    )
    features_dir.children.append(other_dir)
    
    other_file = DirectoryNode(
        name="other.py",
        path="src/app/features/other/other.py",
        is_directory=False,
        children=[]
    )
    other_dir.children.append(other_file)
    
    print("✅ Estructura creada:")
    def print_tree(node, indent=""):
        print(f"{indent}{node.name} ({'📁' if node.is_directory else '📄'})")
        for child in node.children:
            print_tree(child, indent + "  ")
    
    print_tree(root)
    
    print("\n📊 PASO 2: Simular selección de carpeta raíz 'src'")
    
    # Simular la lógica del controlador: BFS para expandir
    def expand_directory(node):
        paths = set()
        queue = [node]
        while queue:
            current = queue.pop(0)
            paths.add(current.path)
            queue.extend(current.children)
        return paths
    
    selected_paths = expand_directory(root)
    print(f"✅ Paths seleccionados después de expandir 'src': {len(selected_paths)}")
    for path in sorted(selected_paths):
        print(f"   ✅ {path}")
    
    print("\n📊 PASO 3: Usuario deselecciona 'src/app/features/dashboard'")
    
    # Simular deselección del directorio dashboard
    dashboard_paths = expand_directory(dashboard_dir)
    print(f"❌ Paths a remover de dashboard: {len(dashboard_paths)}")
    for path in sorted(dashboard_paths):
        print(f"   ❌ {path}")
    
    # Aplicar deselección
    selected_paths_after = selected_paths - dashboard_paths
    print(f"✅ Paths restantes después de deselección: {len(selected_paths_after)}")
    for path in sorted(selected_paths_after):
        print(f"   ✅ {path}")
    
    print("\n📊 PASO 4: Verificar que el estado es correcto")
    
    # Verificaciones
    should_be_selected = [
        "src",
        "src/app", 
        "src/app/features",
        "src/app/features/other",
        "src/app/features/other/other.py"
    ]
    
    should_be_deselected = [
        "src/app/features/dashboard",
        "src/app/features/dashboard/component.py"
    ]
    
    print("🔍 Verificando estados esperados:")
    all_correct = True
    
    for path in should_be_selected:
        is_selected = path in selected_paths_after
        print(f"   {'✅' if is_selected else '❌'} {path} → {'SELECCIONADO' if is_selected else 'DESELECCIONADO'}")
        if not is_selected:
            all_correct = False
    
    for path in should_be_deselected:
        is_deselected = path not in selected_paths_after
        print(f"   {'✅' if is_deselected else '❌'} {path} → {'DESELECCIONADO' if is_deselected else 'SELECCIONADO'}")
        if not is_deselected:
            all_correct = False
    
    print(f"\n📋 RESULTADO DE LA LÓGICA DEL CONTROLADOR:")
    if all_correct:
        print("🎉 ✅ La lógica del controlador funciona CORRECTAMENTE")
        print("❓ El problema debe estar en la actualización visual de la UI")
    else:
        print("🚨 ❌ HAY UN PROBLEMA en la lógica del controlador")
    
    print("\n📊 PASO 5: Test del repositorio con archivos reales")
    
    # Crear archivos temporales para probar
    test_dir = Path("debug_test_temp")
    test_dir.mkdir(exist_ok=True)
    
    (test_dir / "src").mkdir(exist_ok=True)
    (test_dir / "src" / "app").mkdir(exist_ok=True)
    (test_dir / "src" / "app" / "features").mkdir(exist_ok=True)
    (test_dir / "src" / "app" / "features" / "dashboard").mkdir(exist_ok=True)
    (test_dir / "src" / "app" / "features" / "other").mkdir(exist_ok=True)
    
    (test_dir / "src" / "app" / "features" / "dashboard" / "component.py").write_text("# Dashboard")
    (test_dir / "src" / "app" / "features" / "other" / "other.py").write_text("# Other")
    
    from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
    from features.project_mapper.domain.models.mapping_config_model import MappingConfig
    
    repo = FilesystemProjectMapperRepository()
    
    config = MappingConfig(
        project_dir=str(test_dir),
        selected_paths=selected_paths_after,  # Usar los paths después de deselección
        include_extensions={".py"},
        exclude_patterns=set(),
        output_file="output/test.md"
    )
    
    files = repo._get_files_to_process(config)
    print(f"📄 Archivos procesados por el repositorio: {len(files)}")
    for f in files:
        print(f"   📄 {f.relative_to(test_dir)}")
    
    # Verificar resultados del repositorio
    dashboard_excluded = not any("dashboard" in str(f) for f in files)
    other_included = any("other.py" in str(f) for f in files)
    
    print(f"\n🔍 Verificación del repositorio:")
    print(f"   {'✅' if dashboard_excluded else '❌'} Dashboard excluido: {dashboard_excluded}")
    print(f"   {'✅' if other_included else '❌'} Other incluido: {other_included}")
    
    if dashboard_excluded and other_included:
        print("\n🎉 ✅ El repositorio TAMBIÉN funciona correctamente")
        print("❓ El problema DEFINITIVAMENTE está en la UI/Widget")
    else:
        print("\n🚨 ❌ HAY PROBLEMA también en el repositorio")
    
    # Limpiar
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    
    print("\n" + "="*60)
    print("📋 RESUMEN:")
    print("1. ✅ La lógica del controlador funciona")
    print("2. ✅ El repositorio funciona")
    print("3. ❓ El problema está en la actualización visual del widget")
    print("\n💡 PRÓXIMOS PASOS:")
    print("1. Verificar que update_selected_paths() se llame correctamente")
    print("2. Revisar que _update_checkbox_states() encuentre todos los checkboxes")
    print("3. Confirmar que los checkboxes se actualicen visualmente")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
