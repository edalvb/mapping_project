#!/usr/bin/env python3
"""
Script de prueba para verificar que los cambios realizados al modelo funcionan correctamente.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Importar las clases modificadas
    from features.project_mapper.domain.models.directory_node_model import DirectoryNode
    from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
    from features.project_mapper.domain.models.mapping_config_model import MappingConfig
    
    print("✅ Todas las importaciones funcionan correctamente")
    
    # Probar crear un DirectoryNode con el nuevo campo is_directory
    test_dir = DirectoryNode(
        name="test_folder", 
        path="test_folder", 
        is_directory=True
    )
    test_file = DirectoryNode(
        name="test_file.py", 
        path="test_folder/test_file.py", 
        is_directory=False,
        parent=test_dir
    )
    test_dir.children.append(test_file)
    
    print(f"✅ DirectoryNode creado: {test_dir.name} (directorio: {test_dir.is_directory})")
    print(f"✅ Archivo hijo creado: {test_file.name} (directorio: {test_file.is_directory})")
    
    # Probar crear un MappingConfig con selected_paths
    config = MappingConfig(
        project_dir="/test",
        selected_paths={"test_folder", "test_folder/test_file.py"},
        include_extensions={".py"},
        exclude_patterns={".pyc"},
        output_file="/test/output.md"
    )
    
    print(f"✅ MappingConfig creado con selected_paths: {config.selected_paths}")
    
    print("\n🎉 Todos los cambios funcionan correctamente!")
    
except Exception as e:
    print(f"❌ Error encontrado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
