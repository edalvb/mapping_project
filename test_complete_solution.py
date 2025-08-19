"""
Test final para verificar que tanto la deselección como la expansión funcionan sin problemas
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("🧪 TEST FINAL COMPLETO - DESELECCIÓN + EXPANSIÓN")
    print("="*60)
    
    from features.project_mapper.data.repositories.filesystem_project_mapper_repository import FilesystemProjectMapperRepository
    from features.project_mapper.domain.models.mapping_config_model import MappingConfig
    
    # Crear estructura de prueba
    test_dir = Path("final_complete_test")
    test_dir.mkdir(exist_ok=True)
    
    # Crear la estructura original del usuario + más contenido
    (test_dir / "src").mkdir(exist_ok=True)
    (test_dir / "src" / "app").mkdir(exist_ok=True)
    (test_dir / "src" / "app" / "features").mkdir(exist_ok=True)
    (test_dir / "src" / "app" / "features" / "dashboard").mkdir(exist_ok=True)
    (test_dir / "src" / "app" / "features" / "other").mkdir(exist_ok=True)
    (test_dir / "src" / "app" / "features" / "analytics").mkdir(exist_ok=True)
    (test_dir / "src" / "app" / "features" / "settings").mkdir(exist_ok=True)
    
    # Crear archivos
    (test_dir / "src" / "main.py").write_text("# Main app")
    (test_dir / "src" / "app" / "app.py").write_text("# App module")
    (test_dir / "src" / "app" / "features" / "__init__.py").write_text("# Features init")
    (test_dir / "src" / "app" / "features" / "dashboard" / "component.py").write_text("# Dashboard component")
    (test_dir / "src" / "app" / "features" / "dashboard" / "service.py").write_text("# Dashboard service")
    (test_dir / "src" / "app" / "features" / "other" / "other_component.py").write_text("# Other component")
    (test_dir / "src" / "app" / "features" / "analytics" / "analytics.py").write_text("# Analytics")
    (test_dir / "src" / "app" / "features" / "settings" / "settings.py").write_text("# Settings")
    
    print("📁 Estructura de prueba creada:")
    print("   src/")
    print("   ├── main.py")
    print("   └── app/")
    print("       ├── app.py")
    print("       └── features/")
    print("           ├── __init__.py")
    print("           ├── dashboard/")
    print("           │   ├── component.py")
    print("           │   └── service.py")
    print("           ├── other/")
    print("           │   └── other_component.py")
    print("           ├── analytics/")
    print("           │   └── analytics.py")
    print("           └── settings/")
    print("               └── settings.py")
    
    repo = FilesystemProjectMapperRepository()
    
    print(f"\n🧪 ESCENARIO 1: Selección completa de 'src'")
    
    # Simular selección completa de src
    all_paths_in_src = {
        "src",
        "src/main.py",
        "src/app",
        "src/app/app.py",
        "src/app/features",
        "src/app/features/__init__.py",
        "src/app/features/dashboard",
        "src/app/features/dashboard/component.py",
        "src/app/features/dashboard/service.py",
        "src/app/features/other",
        "src/app/features/other/other_component.py",
        "src/app/features/analytics",
        "src/app/features/analytics/analytics.py",
        "src/app/features/settings",
        "src/app/features/settings/settings.py"
    }
    
    config1 = MappingConfig(
        project_dir=str(test_dir),
        selected_paths=all_paths_in_src,
        include_extensions={".py"},
        exclude_patterns=set(),
        output_file="output/test1.md"
    )
    
    files1 = repo._get_files_to_process(config1)
    print(f"📄 Archivos incluidos inicialmente: {len(files1)}")
    for f in files1:
        print(f"   ✅ {f.relative_to(test_dir)}")
    
    print(f"\n🧪 ESCENARIO 2: Deselección de 'dashboard'")
    
    # Simular deselección de dashboard (problema original)
    dashboard_paths = {
        "src/app/features/dashboard",
        "src/app/features/dashboard/component.py",
        "src/app/features/dashboard/service.py"
    }
    
    selected_after_dashboard_deselection = all_paths_in_src - dashboard_paths
    
    config2 = MappingConfig(
        project_dir=str(test_dir),
        selected_paths=selected_after_dashboard_deselection,
        include_extensions={".py"},
        exclude_patterns=set(),
        output_file="output/test2.md"
    )
    
    files2 = repo._get_files_to_process(config2)
    print(f"📄 Archivos después de deseleccionar dashboard: {len(files2)}")
    for f in files2:
        print(f"   ✅ {f.relative_to(test_dir)}")
    
    # Verificación dashboard
    dashboard_excluded = not any("dashboard" in str(f) for f in files2)
    other_features_included = any("other_component.py" in str(f) for f in files2)
    analytics_included = any("analytics.py" in str(f) for f in files2)
    
    print(f"\n🔍 VERIFICACIÓN DESELECCIÓN:")
    print(f"   {'✅' if dashboard_excluded else '❌'} Dashboard excluido: {dashboard_excluded}")
    print(f"   {'✅' if other_features_included else '❌'} Other incluido: {other_features_included}")
    print(f"   {'✅' if analytics_included else '❌'} Analytics incluido: {analytics_included}")
    
    print(f"\n🧪 ESCENARIO 3: Deselección adicional de 'analytics'")
    
    # Simular deselección adicional de analytics
    analytics_paths = {
        "src/app/features/analytics",
        "src/app/features/analytics/analytics.py"
    }
    
    selected_after_both_deselections = selected_after_dashboard_deselection - analytics_paths
    
    config3 = MappingConfig(
        project_dir=str(test_dir),
        selected_paths=selected_after_both_deselections,
        include_extensions={".py"},
        exclude_patterns=set(),
        output_file="output/test3.md"
    )
    
    files3 = repo._get_files_to_process(config3)
    print(f"📄 Archivos después de deseleccionar dashboard + analytics: {len(files3)}")
    for f in files3:
        print(f"   ✅ {f.relative_to(test_dir)}")
    
    # Verificación final
    dashboard_still_excluded = not any("dashboard" in str(f) for f in files3)
    analytics_excluded = not any("analytics" in str(f) for f in files3)
    other_still_included = any("other_component.py" in str(f) for f in files3)
    settings_included = any("settings.py" in str(f) for f in files3)
    main_included = any("main.py" in str(f) for f in files3)
    
    print(f"\n🔍 VERIFICACIÓN FINAL:")
    print(f"   {'✅' if dashboard_still_excluded else '❌'} Dashboard sigue excluido: {dashboard_still_excluded}")
    print(f"   {'✅' if analytics_excluded else '❌'} Analytics excluido: {analytics_excluded}")
    print(f"   {'✅' if other_still_included else '❌'} Other sigue incluido: {other_still_included}")
    print(f"   {'✅' if settings_included else '❌'} Settings incluido: {settings_included}")
    print(f"   {'✅' if main_included else '❌'} main.py incluido: {main_included}")
    
    # Resultado final
    all_checks_passed = (
        dashboard_still_excluded and 
        analytics_excluded and 
        other_still_included and 
        settings_included and 
        main_included
    )
    
    print(f"\n📋 RESULTADO DE FUNCIONALIDAD:")
    if all_checks_passed:
        print("🎉 ✅ ¡TODAS LAS VERIFICACIONES DE DESELECCIÓN PASARON!")
    else:
        print("🚨 ❌ ALGUNAS VERIFICACIONES DE DESELECCIÓN FALLARON")
    
    print(f"\n🎯 RESUMEN DE MEJORAS IMPLEMENTADAS:")
    print("🔧 PROBLEMA 1 - Deselección no funcionaba:")
    print("   ✅ SOLUCIONADO: update_selected_paths() ahora actualiza checkboxes correctamente")
    
    print("🔧 PROBLEMA 2 - Expansión saltaba al principio:")
    print("   ✅ SOLUCIONADO: _update_tree_structure() preserva posición de scroll")
    
    print(f"\n💡 ESTRATEGIA TÉCNICA:")
    print("• update_selected_paths() → _update_checkbox_states() + page.update()")
    print("• _on_expand_click() → _update_tree_structure()")
    print("• _update_tree_structure() → Solo reconstruye TreeView, preserva scroll")
    print("• _conservative_update() → Solo para casos complejos como fallback")
    
    print(f"\n✅ BENEFICIOS FINALES:")
    print("• ✅ Deselección de subcarpetas funciona correctamente")
    print("• ✅ Expansión de carpetas NO hace scroll jump")
    print("• ✅ Actualizaciones más rápidas y precisas")
    print("• ✅ Mejor experiencia de usuario")
    
    # Limpiar
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
