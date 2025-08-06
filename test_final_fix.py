"""
Prueba final específica para verificar la corrección completa
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
    from features.project_mapper.domain.models.mapping_config_model import MappingConfig
    
    print("✅ PRUEBA FINAL DE CORRECCIÓN")
    
    # Usar el directorio actual del proyecto como prueba
    project_dir = "."
    
    # CASO 1: Solo directorio src seleccionado
    print(f"\n🧪 CASO 1: Solo directorio 'src' seleccionado")
    
    config1 = MappingConfig(
        project_dir=project_dir,
        selected_paths={"src"},
        include_extensions={".py"},
        exclude_patterns=set(),
        output_file="output/test1.md"
    )
    
    repo = FilesystemProjectMapperRepository()
    files1 = repo._get_files_to_process(config1)
    
    print(f"📄 Archivos encontrados: {len(files1)}")
    for f in files1[:5]:  # Mostrar primeros 5
        print(f"   📄 {f.relative_to(Path(project_dir))}")
    if len(files1) > 5:
        print(f"   ... y {len(files1) - 5} más")
    
    # CASO 2: Directorio src + archivos específicos seleccionados  
    print(f"\n🧪 CASO 2: Directorio 'src' + archivos específicos seleccionados")
    
    # Encontrar algunos archivos específicos en src
    src_files = [f for f in files1 if f.name.endswith('.py')]
    specific_files = [str(f.relative_to(Path(project_dir))) for f in src_files[:2]]  # Primeros 2
    
    config2 = MappingConfig(
        project_dir=project_dir,
        selected_paths={"src"} | set(specific_files),
        include_extensions={".py"},
        exclude_patterns=set(),
        output_file="output/test2.md"
    )
    
    files2 = repo._get_files_to_process(config2)
    
    print(f"✅ Archivos específicos seleccionados: {specific_files}")
    print(f"📄 Archivos encontrados: {len(files2)}")
    
    # Verificar si los archivos específicos están incluidos
    for specific_file in specific_files:
        specific_path = Path(project_dir) / specific_file
        included = specific_path in files2
        print(f"   {'✅' if included else '❌'} {specific_file}: {'INCLUIDO' if included else 'NO INCLUIDO'}")
    
    # CASO 3: Directorio src seleccionado, algunos archivos específicos deseleccionados
    print(f"\n🧪 CASO 3: Directorio 'src' seleccionado, un archivo específico deseleccionado")
    
    # Seleccionar directorio + algunos archivos específicos (simulando deselección)
    selected_specific = specific_files[1:] if len(specific_files) > 1 else []  # Excluir el primero
    deselected_file = specific_files[0] if specific_files else None
    
    config3 = MappingConfig(
        project_dir=project_dir,
        selected_paths={"src"} | set(selected_specific),
        include_extensions={".py"},
        exclude_patterns=set(),
        output_file="output/test3.md"
    )
    
    files3 = repo._get_files_to_process(config3)
    
    print(f"❌ Archivo deseleccionado: {deselected_file}")
    print(f"✅ Archivos específicos seleccionados: {selected_specific}")
    print(f"📄 Archivos encontrados: {len(files3)}")
    
    if deselected_file:
        deselected_path = Path(project_dir) / deselected_file
        deselected_included = deselected_path in files3
        print(f"   {'❌ PROBLEMA' if deselected_included else '✅ CORRECTO'}: Archivo deseleccionado {deselected_file} {'incluido' if deselected_included else 'no incluido'}")
    
    for specific_file in selected_specific:
        specific_path = Path(project_dir) / specific_file
        included = specific_path in files3
        print(f"   {'✅' if included else '❌'} {specific_file}: {'INCLUIDO' if included else 'NO INCLUIDO'}")
    
    print(f"\n📋 RESUMEN:")
    caso1_ok = len(files1) > 0
    caso2_ok = all(Path(project_dir) / f in files2 for f in specific_files)
    caso3_ok = True
    if deselected_file:
        deselected_path = Path(project_dir) / deselected_file
        caso3_ok = deselected_path not in files3
    
    print(f"✅ Caso 1 (solo directorio): {'CORRECTO' if caso1_ok else 'INCORRECTO'}")
    print(f"✅ Caso 2 (archivos específicos): {'CORRECTO' if caso2_ok else 'INCORRECTO'}")
    print(f"✅ Caso 3 (deselección): {'CORRECTO' if caso3_ok else 'INCORRECTO'}")
    
    if caso1_ok and caso2_ok and caso3_ok:
        print(f"🎉 ¡TODAS LAS PRUEBAS PASARON! La corrección funciona correctamente.")
    else:
        print(f"❌ Algunas pruebas fallaron. Revisar la lógica.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
