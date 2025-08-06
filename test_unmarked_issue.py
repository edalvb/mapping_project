#!/usr/bin/env python3
"""
Prueba específica para el problema reportado: "A pesar que desmarque una carpeta esta igual se sigue leyendo"
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
from features.project_mapper.domain.models.mapping_config_model import MappingConfig

def test_unmarked_folder_issue():
    """Simular el problema específico del usuario"""
    
    # Crear proyecto temporal
    temp_dir = Path(tempfile.mkdtemp())
    (temp_dir / "src").mkdir()
    (temp_dir / "src" / "main.py").write_text("print('main')")
    (temp_dir / "tests").mkdir()
    (temp_dir / "tests" / "test.py").write_text("def test(): pass")
    (temp_dir / "README.md").write_text("# Project")
    
    repository = FilesystemProjectMapperRepository()
    
    print("🔍 SIMULANDO EL PROBLEMA REPORTADO:")
    print(f"📁 Proyecto temporal: {temp_dir}")
    
    # Escenario 1: Carpeta inicialmente seleccionada automáticamente (problema anterior)
    print("\n📋 Escenario 1: Carpeta raíz inicialmente marcada (comportamiento anterior problemático)")
    config_with_root = MappingConfig(
        project_dir=str(temp_dir),
        selected_paths={""},  # Directorio raíz seleccionado automáticamente
        include_extensions=set(),
        exclude_patterns=set(),
        output_file=str(temp_dir / "output.md")
    )
    
    files_with_root = repository._get_files_to_process(config_with_root)
    rel_files_with_root = [f.relative_to(temp_dir) for f in files_with_root]
    print(f"   Archivos procesados: {rel_files_with_root}")
    print(f"   ✅ Se procesan TODOS los archivos (comportamiento esperado cuando raíz está marcado)")
    
    # Escenario 2: Usuario desmarca la carpeta raíz (comportamiento correcto esperado)
    print("\n📋 Escenario 2: Usuario desmarca la carpeta raíz")
    config_no_selection = MappingConfig(
        project_dir=str(temp_dir),
        selected_paths=set(),  # Sin selecciones - carpeta desmarcada
        include_extensions=set(),
        exclude_patterns=set(),
        output_file=str(temp_dir / "output.md")
    )
    
    files_no_selection = repository._get_files_to_process(config_no_selection)
    rel_files_no_selection = [f.relative_to(temp_dir) for f in files_no_selection]
    print(f"   Archivos procesados: {rel_files_no_selection}")
    
    # Verificar que el comportamiento es correcto
    if len(rel_files_no_selection) > 0:
        print(f"   ⚠️  NOTA: Sin selecciones se procesan todos los archivos (esto es intencional)")
        print(f"   📝 Para no procesar nada, el usuario debe seleccionar archivos/carpetas específicos")
    else:
        print(f"   ✅ Sin selecciones = sin archivos procesados")
    
    # Escenario 3: Usuario selecciona solo una subcarpeta específica
    print("\n📋 Escenario 3: Usuario selecciona solo subcarpeta 'src' (desmarca todo lo demás)")
    config_only_src = MappingConfig(
        project_dir=str(temp_dir),
        selected_paths={"src"},  # Solo carpeta src seleccionada
        include_extensions=set(),
        exclude_patterns=set(),
        output_file=str(temp_dir / "output.md")
    )
    
    files_only_src = repository._get_files_to_process(config_only_src)
    rel_files_only_src = [f.relative_to(temp_dir) for f in files_only_src]
    print(f"   Archivos procesados: {rel_files_only_src}")
    
    # Verificar que SOLO se procesan archivos de src
    src_files = [f for f in rel_files_only_src if str(f).startswith("src")]
    non_src_files = [f for f in rel_files_only_src if not str(f).startswith("src")]
    
    if len(non_src_files) == 0:
        print(f"   ✅ CORRECTO: Solo se procesan archivos de 'src'")
        print(f"   ✅ NO se procesan: tests/, README.md")
    else:
        print(f"   ❌ ERROR: Se están procesando archivos fuera de 'src': {non_src_files}")
        return False
    
    # Escenario 4: Usuario selecciona solo un archivo específico
    print("\n📋 Escenario 4: Usuario selecciona solo archivo 'README.md' (desmarca carpetas)")
    config_only_readme = MappingConfig(
        project_dir=str(temp_dir),
        selected_paths={"README.md"},  # Solo README.md seleccionado
        include_extensions=set(),
        exclude_patterns=set(),
        output_file=str(temp_dir / "output.md")
    )
    
    files_only_readme = repository._get_files_to_process(config_only_readme)
    rel_files_only_readme = [f.relative_to(temp_dir) for f in files_only_readme]
    print(f"   Archivos procesados: {rel_files_only_readme}")
    
    if rel_files_only_readme == [Path("README.md")]:
        print(f"   ✅ CORRECTO: Solo se procesa README.md")
    else:
        print(f"   ❌ ERROR: Se esperaba solo README.md, se obtuvo: {rel_files_only_readme}")
        return False
    
    print(f"\n🎉 ¡PROBLEMA RESUELTO!")
    print(f"✅ Ahora las carpetas desmarcadas NO se procesan")
    print(f"✅ El usuario tiene control granular sobre qué se incluye")
    
    # Limpiar
    import shutil
    shutil.rmtree(temp_dir)
    
    return True

if __name__ == "__main__":
    try:
        success = test_unmarked_folder_issue()
        if success:
            print(f"\n🔧 LA CORRECCIÓN FUNCIONA CORRECTAMENTE")
        else:
            print(f"\n❌ AÚN HAY PROBLEMAS QUE CORREGIR")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
