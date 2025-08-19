"""
Test para verificar si el problema está en la actualización visual de los checkboxes
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("🔍 ANALIZANDO PROBLEMA DE ACTUALIZACIÓN VISUAL")
    
    # Simular estado inicial: carpeta raíz seleccionada
    initial_selected_paths = {
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
        "src/app/features/other/other.py"
    }
    
    print(f"📊 ESTADO INICIAL - Carpeta 'src' seleccionada:")
    print(f"   Paths seleccionados: {len(initial_selected_paths)}")
    for path in sorted(initial_selected_paths):
        print(f"   ✅ {path}")
    
    # Simular deselección de dashboard
    print(f"\n🎯 USUARIO DESELECCIONA: 'src/app/features/dashboard'")
    
    # Paths que deberían ser removidos (directorio + todos sus hijos)
    dashboard_paths = {
        "src/app/features/dashboard",
        "src/app/features/dashboard/component.py",
        "src/app/features/dashboard/service.py"
    }
    
    print(f"❌ Paths que deben ser removidos:")
    for path in sorted(dashboard_paths):
        print(f"   - {path}")
    
    # Estado después de deselección
    final_selected_paths = initial_selected_paths - dashboard_paths
    
    print(f"\n📊 ESTADO FINAL - Después de deselección:")
    print(f"   Paths seleccionados: {len(final_selected_paths)}")
    for path in sorted(final_selected_paths):
        print(f"   ✅ {path}")
    
    # Verificar qué checkboxes deberían estar marcados
    print(f"\n🔍 VERIFICACIÓN DE CHECKBOXES:")
    
    test_paths = [
        "src",                                   # Carpeta padre - debería seguir seleccionada
        "src/main.py",                           # Archivo en raíz - debería seguir seleccionado
        "src/app",                               # Carpeta app - debería seguir seleccionada
        "src/app/features",                      # Carpeta features - debería seguir seleccionada
        "src/app/features/__init__.py",          # Archivo init - debería seguir seleccionado
        "src/app/features/dashboard",            # Carpeta dashboard - DEBERÍA ESTAR DESELECCIONADA
        "src/app/features/dashboard/component.py", # Archivo dashboard - DEBERÍA ESTAR DESELECCIONADO
        "src/app/features/other",                # Carpeta other - debería seguir seleccionada
        "src/app/features/other/other.py"       # Archivo other - debería seguir seleccionado
    ]
    
    for path in test_paths:
        is_selected = path in final_selected_paths
        should_be_checked = is_selected
        status = "✅ SELECCIONADO" if should_be_checked else "❌ DESELECCIONADO"
        icon = "📁" if "/" in path and not path.endswith(".py") else "📄"
        print(f"   {icon} {path:<40} → {status}")
    
    print(f"\n🎯 POSIBLES PROBLEMAS:")
    print(f"1. El checkbox de 'src/app/features/dashboard' no se actualiza visualmente")
    print(f"2. Los checkboxes de archivos dentro de dashboard no se actualizan")
    print(f"3. El widget no llama a update_selected_paths() correctamente")
    print(f"4. El método _update_checkbox_states() no encuentra todos los checkboxes")
    
    print(f"\n💡 PARA VERIFICAR:")
    print(f"1. Revisar si on_node_toggle() se ejecuta correctamente")
    print(f"2. Verificar si el controlador actualiza self.state.selected_paths")
    print(f"3. Confirmar si view.update_view(preserve_expansion_state=True) se llama")
    print(f"4. Verificar si update_selected_paths() actualiza todos los checkboxes")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
