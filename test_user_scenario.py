"""
Test específico para el problema reportado por el usuario
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
    from features.project_mapper.domain.models.mapping_config_model import MappingConfig
    from features.project_mapper.domain.models.directory_node_model import DirectoryNode
    
    print("🔍 REPRODUCIENDO PROBLEMA ESPECÍFICO DEL USUARIO")
    print("Escenario: Seleccionar 'src' raíz, luego deseleccionar 'src/app/features/dashboard'")
    
    # Crear estructura como la del usuario
    test_dir = Path("test_user_scenario")
    test_dir.mkdir(exist_ok=True)
    
    # Crear estructura src/app/features/dashboard
    (test_dir / "src").mkdir(exist_ok=True)
    (test_dir / "src" / "app").mkdir(exist_ok=True)
    (test_dir / "src" / "app" / "features").mkdir(exist_ok=True)
    (test_dir / "src" / "app" / "features" / "dashboard").mkdir(exist_ok=True)
    (test_dir / "src" / "app" / "features" / "other").mkdir(exist_ok=True)
    
    # Crear archivos
    (test_dir / "src" / "main.py").write_text("# Main")
    (test_dir / "src" / "app" / "app.py").write_text("# App")
    (test_dir / "src" / "app" / "features" / "__init__.py").write_text("# Features init")
    (test_dir / "src" / "app" / "features" / "dashboard" / "component.py").write_text("# Dashboard component")
    (test_dir / "src" / "app" / "features" / "dashboard" / "service.py").write_text("# Dashboard service")
    (test_dir / "src" / "app" / "features" / "other" / "other.py").write_text("# Other feature")
    
    print(f"📁 Estructura creada:")
    print("   src/")
    print("   ├── main.py")
    print("   └── app/")
    print("       ├── app.py")
    print("       └── features/")
    print("           ├── __init__.py")
    print("           ├── dashboard/")
    print("           │   ├── component.py")
    print("           │   └── service.py")
    print("           └── other/")
    print("               └── other.py")
    
    # Simular el árbol de directorios como lo construiría el sistema
    def create_directory_tree():
        root = DirectoryNode(
            name="src",
            path="src",
            is_directory=True,
            children=[]
        )
        
        # src/main.py
        main_file = DirectoryNode(
            name="main.py",
            path="src/main.py",
            is_directory=False,
            children=[]
        )
        root.children.append(main_file)
        
        # src/app/
        app_dir = DirectoryNode(
            name="app",
            path="src/app",
            is_directory=True,
            children=[]
        )
        root.children.append(app_dir)
        
        # src/app/app.py
        app_file = DirectoryNode(
            name="app.py",
            path="src/app/app.py",
            is_directory=False,
            children=[]
        )
        app_dir.children.append(app_file)
        
        # src/app/features/
        features_dir = DirectoryNode(
            name="features",
            path="src/app/features",
            is_directory=True,
            children=[]
        )
        app_dir.children.append(features_dir)
        
        # src/app/features/__init__.py
        init_file = DirectoryNode(
            name="__init__.py",
            path="src/app/features/__init__.py",
            is_directory=False,
            children=[]
        )
        features_dir.children.append(init_file)
        
        # src/app/features/dashboard/
        dashboard_dir = DirectoryNode(
            name="dashboard",
            path="src/app/features/dashboard",
            is_directory=True,
            children=[]
        )
        features_dir.children.append(dashboard_dir)
        
        # src/app/features/dashboard/component.py
        comp_file = DirectoryNode(
            name="component.py",
            path="src/app/features/dashboard/component.py",
            is_directory=False,
            children=[]
        )
        dashboard_dir.children.append(comp_file)
        
        # src/app/features/dashboard/service.py
        service_file = DirectoryNode(
            name="service.py",
            path="src/app/features/dashboard/service.py",
            is_directory=False,
            children=[]
        )
        dashboard_dir.children.append(service_file)
        
        # src/app/features/other/
        other_dir = DirectoryNode(
            name="other",
            path="src/app/features/other",
            is_directory=True,
            children=[]
        )
        features_dir.children.append(other_dir)
        
        # src/app/features/other/other.py
        other_file = DirectoryNode(
            name="other.py",
            path="src/app/features/other/other.py",
            is_directory=False,
            children=[]
        )
        other_dir.children.append(other_file)
        
        return root
    
    # Simular función del controlador para expandir directorio
    def simulate_controller_expansion(node):
        """Simula la lógica del controlador: BFS para expandir todos los hijos"""
        paths_to_change = set()
        q = [node]
        while q:
            curr = q.pop(0)
            paths_to_change.add(curr.path)
            q.extend(curr.children)
        return paths_to_change
    
    tree = create_directory_tree()
    repo = FilesystemProjectMapperRepository()
    
    print(f"\n🧪 PASO 1: Usuario selecciona carpeta raíz 'src'")
    # Cuando usuario selecciona "src", el controlador expande todo
    expanded_paths = simulate_controller_expansion(tree)
    print(f"✅ Controlador expande a {len(expanded_paths)} paths:")
    for path in sorted(expanded_paths):
        print(f"   + {path}")
    
    config1 = MappingConfig(
        project_dir=str(test_dir),
        selected_paths=expanded_paths,
        include_extensions={".py"},
        exclude_patterns=set(),
        output_file="output/test1.md"
    )
    
    files1 = repo._get_files_to_process(config1)
    print(f"📄 Archivos encontrados: {len(files1)}")
    for f in files1:
        print(f"   📄 {f.relative_to(test_dir)}")
    
    print(f"\n🧪 PASO 2: Usuario deselecciona 'src/app/features/dashboard'")
    # Usuario deselecciona la carpeta dashboard
    dashboard_node = None
    for child in tree.children:  # app
        if child.name == "app":
            for grandchild in child.children:  # features
                if grandchild.name == "features":
                    for ggchild in grandchild.children:  # dashboard
                        if ggchild.name == "dashboard":
                            dashboard_node = ggchild
                            break
    
    if dashboard_node:
        # Simular deselección: quitar todos los paths de dashboard
        dashboard_paths = simulate_controller_expansion(dashboard_node)
        deselected_paths = expanded_paths - dashboard_paths
        
        print(f"❌ Controlador quita {len(dashboard_paths)} paths de dashboard:")
        for path in sorted(dashboard_paths):
            print(f"   - {path}")
        
        print(f"✅ Quedan {len(deselected_paths)} paths seleccionados")
        
        config2 = MappingConfig(
            project_dir=str(test_dir),
            selected_paths=deselected_paths,
            include_extensions={".py"},
            exclude_patterns=set(),
            output_file="output/test2.md"
        )
        
        files2 = repo._get_files_to_process(config2)
        print(f"📄 Archivos encontrados después de deselección: {len(files2)}")
        for f in files2:
            print(f"   📄 {f.relative_to(test_dir)}")
        
        # Verificar resultados
        dashboard_excluded = not any("dashboard" in str(f) for f in files2)
        other_included = any("other.py" in str(f) for f in files2)
        main_included = any("main.py" in str(f) for f in files2)
        
        print(f"\n📋 VERIFICACIÓN:")
        print(f"✅ Dashboard excluido: {'SÍ' if dashboard_excluded else 'NO ❌'}")
        print(f"✅ Other feature incluido: {'SÍ' if other_included else 'NO ❌'}")
        print(f"✅ main.py incluido: {'SÍ' if main_included else 'NO ❌'}")
        
        if dashboard_excluded and other_included and main_included:
            print(f"\n🎉 ¡FUNCIONA CORRECTAMENTE!")
            print(f"El problema reportado NO se reproduce.")
        else:
            print(f"\n🚨 PROBLEMA CONFIRMADO")
            print(f"La deselección no está funcionando correctamente.")
    
    # Limpiar
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
