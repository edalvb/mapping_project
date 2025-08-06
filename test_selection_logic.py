#!/usr/bin/env python3
"""
Script de prueba para verificar que la lógica de selección de archivos funciona correctamente.
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
from features.project_mapper.domain.models.mapping_config_model import MappingConfig

def create_test_project():
    """Crear un proyecto de prueba temporal"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Crear estructura de carpetas y archivos
    (temp_dir / "src").mkdir()
    (temp_dir / "src" / "main.py").write_text("print('main')")
    (temp_dir / "src" / "utils.py").write_text("def helper(): pass")
    
    (temp_dir / "tests").mkdir()
    (temp_dir / "tests" / "test_main.py").write_text("def test_main(): pass")
    
    (temp_dir / "docs").mkdir()
    (temp_dir / "docs" / "readme.md").write_text("# Documentation")
    
    (temp_dir / "config.json").write_text('{"setting": "value"}')
    
    return temp_dir

def test_selection_logic():
    """Probar la lógica de selección"""
    temp_project = create_test_project()
    repository = FilesystemProjectMapperRepository()
    
    print(f"📁 Proyecto de prueba creado en: {temp_project}")
    print("Estructura del proyecto:")
    for item in sorted(temp_project.rglob("*")):
        if item.is_file():
            rel_path = item.relative_to(temp_project)
            print(f"  📄 {rel_path}")
    
    print("\n" + "="*50)
    
    # Caso 1: Seleccionar solo la carpeta src
    print("🧪 CASO 1: Seleccionar solo carpeta 'src'")
    config1 = MappingConfig(
        project_dir=str(temp_project),
        selected_paths={"src"},
        include_extensions=set(),
        exclude_patterns=set(),
        output_file=str(temp_project / "test1.md")
    )
    
    files1 = repository._get_files_to_process(config1)
    rel_files1 = [f.relative_to(temp_project) for f in files1]
    print(f"Archivos procesados: {rel_files1}")
    expected1 = [Path("src/main.py"), Path("src/utils.py")]
    assert all(f in rel_files1 for f in expected1), f"Esperaba {expected1}, obtuvo {rel_files1}"
    assert Path("tests/test_main.py") not in rel_files1, "No debería incluir archivos de tests"
    assert Path("config.json") not in rel_files1, "No debería incluir config.json"
    print("✅ Caso 1 PASADO")
    
    # Caso 2: Seleccionar archivo individual
    print("\n🧪 CASO 2: Seleccionar solo archivo 'config.json'")
    config2 = MappingConfig(
        project_dir=str(temp_project),
        selected_paths={"config.json"},
        include_extensions=set(),
        exclude_patterns=set(),
        output_file=str(temp_project / "test2.md")
    )
    
    files2 = repository._get_files_to_process(config2)
    rel_files2 = [f.relative_to(temp_project) for f in files2]
    print(f"Archivos procesados: {rel_files2}")
    expected2 = [Path("config.json")]
    assert rel_files2 == expected2, f"Esperaba {expected2}, obtuvo {rel_files2}"
    print("✅ Caso 2 PASADO")
    
    # Caso 3: Mezclar carpetas y archivos
    print("\n🧪 CASO 3: Seleccionar carpeta 'src' y archivo 'config.json'")
    config3 = MappingConfig(
        project_dir=str(temp_project),
        selected_paths={"src", "config.json"},
        include_extensions=set(),
        exclude_patterns=set(),
        output_file=str(temp_project / "test3.md")
    )
    
    files3 = repository._get_files_to_process(config3)
    rel_files3 = [f.relative_to(temp_project) for f in files3]
    print(f"Archivos procesados: {rel_files3}")
    expected3 = [Path("config.json"), Path("src/main.py"), Path("src/utils.py")]
    assert all(f in rel_files3 for f in expected3), f"Esperaba {expected3}, obtuvo {rel_files3}"
    assert Path("tests/test_main.py") not in rel_files3, "No debería incluir archivos de tests"
    print("✅ Caso 3 PASADO")
    
    # Caso 4: No seleccionar nada (carpeta desmarcada)
    print("\n🧪 CASO 4: No seleccionar nada")
    config4 = MappingConfig(
        project_dir=str(temp_project),
        selected_paths=set(),  # Sin selecciones
        include_extensions=set(),
        exclude_patterns=set(),
        output_file=str(temp_project / "test4.md")
    )
    
    files4 = repository._get_files_to_process(config4)
    rel_files4 = [f.relative_to(temp_project) for f in files4]
    print(f"Archivos procesados: {rel_files4}")
    # Sin selecciones no debería procesar nada
    assert len(rel_files4) == 0, f"Esperaba lista vacía, obtuvo {rel_files4}"
    print("✅ Caso 4 PASADO")
    
    # Caso 5: Directorio raíz seleccionado explícitamente
    print("\n🧪 CASO 5: Seleccionar directorio raíz (path vacío)")
    config5 = MappingConfig(
        project_dir=str(temp_project),
        selected_paths={""},  # Directorio raíz
        include_extensions=set(),
        exclude_patterns=set(),
        output_file=str(temp_project / "test5.md")
    )
    
    files5 = repository._get_files_to_process(config5)
    rel_files5 = [f.relative_to(temp_project) for f in files5]
    print(f"Archivos procesados: {rel_files5}")
    # Directorio raíz seleccionado debería incluir todo
    expected5 = [Path("config.json"), Path("docs/readme.md"), Path("src/main.py"), Path("src/utils.py"), Path("tests/test_main.py")]
    assert all(f in rel_files5 for f in expected5), f"Esperaba {expected5}, obtuvo {rel_files5}"
    print("✅ Caso 5 PASADO")
    
    # Caso 6: Solo archivos específicos (simular desmarcar carpetas)
    print("\n🧪 CASO 6: Solo archivos específicos (carpetas desmarcadas)")
    config6 = MappingConfig(
        project_dir=str(temp_project),
        selected_paths={"src/main.py", "config.json"},  # Solo archivos específicos
        include_extensions=set(),
        exclude_patterns=set(),
        output_file=str(temp_project / "test6.md")
    )
    
    files6 = repository._get_files_to_process(config6)
    rel_files6 = [f.relative_to(temp_project) for f in files6]
    print(f"Archivos procesados: {rel_files6}")
    expected6 = [Path("config.json"), Path("src/main.py")]
    assert sorted(rel_files6) == sorted(expected6), f"Esperaba {expected6}, obtuvo {rel_files6}"
    assert Path("src/utils.py") not in rel_files6, "No debería incluir src/utils.py"
    assert Path("tests/test_main.py") not in rel_files6, "No debería incluir tests/test_main.py"
    print("✅ Caso 6 PASADO")
    
    print("\n🎉 ¡Todos los casos de prueba pasaron!")
    
    # Limpiar
    import shutil
    shutil.rmtree(temp_project)
    print(f"🧹 Limpieza completada")

if __name__ == "__main__":
    try:
        test_selection_logic()
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
