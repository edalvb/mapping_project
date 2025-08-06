# path: build_multi.py
import os
import subprocess
import sys
import argparse


def main():
    """
    Script para construir la aplicación Cortex AI Agent en múltiples plataformas.
    
    Soporta: Windows, Android (APK), Web
    """
    parser = argparse.ArgumentParser(description="Build Cortex AI Agent para múltiples plataformas")
    parser.add_argument(
        "--platform", 
        choices=["windows", "apk", "web", "all"], 
        default="windows",
        help="Plataforma de destino para el build (default: windows)"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Habilitar salida verbose"
    )
    
    args = parser.parse_args()
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"Project Root: {project_root}")

    # 1. Verificar estructura del proyecto
    print("\n--- Verificando estructura del proyecto ---")
    required_paths = {
        "Archivo de configuración": os.path.join(project_root, "pyproject.toml"),
        "Directorio fuente": os.path.join(project_root, "src"),
        "Punto de entrada principal": os.path.join(project_root, "main.py"),
        "Punto de entrada fuente": os.path.join(project_root, "src", "main.py"),
        "Icono de aplicación": os.path.join(project_root, "src", "assets", "app_icon.png"),
    }

    all_paths_ok = True
    for name, path in required_paths.items():
        if not os.path.exists(path):
            print(f"❌ ERROR: {name} no encontrado en: {path}")
            all_paths_ok = False
        else:
            print(f"✅ OK: {name} encontrado.")

    if not all_paths_ok:
        print("\nPor favor corrija los archivos faltantes antes de construir.")
        sys.exit(1)

    print("✅ Estructura del proyecto válida.")

    # 2. Definir plataformas a construir
    platforms_to_build = []
    if args.platform == "all":
        platforms_to_build = ["windows", "apk", "web"]
    else:
        platforms_to_build = [args.platform]

    # 3. Construir para cada plataforma
    for platform in platforms_to_build:
        print(f"\n{'='*60}")
        print(f"🔨 CONSTRUYENDO PARA: {platform.upper()}")
        print(f"{'='*60}")
        
        build_command = [
            "flet",
            "build",
            platform
        ]
        
        if args.verbose:
            build_command.append("-vv")
        
        print(f"Comando: {' '.join(build_command)}")
        
        try:
            process = subprocess.run(
                build_command,
                cwd=project_root,
                check=True,
                text=True,
                encoding='utf-8'
            )
            
            print(f"\n✅ BUILD EXITOSO PARA {platform.upper()}!")
            
            # Información específica por plataforma
            if platform == "windows":
                print(f"📁 Aplicación Windows: {os.path.join(project_root, 'build', 'windows', 'cortex_ai_agent.exe')}")
            elif platform == "apk":
                print(f"📁 APK Android: {os.path.join(project_root, 'build', 'apk')}")
            elif platform == "web":
                print(f"📁 Aplicación Web: {os.path.join(project_root, 'build', 'web')}")
                
        except FileNotFoundError:
            print(f"\n❌ ERROR FATAL: comando 'flet' no encontrado.")
            print("Por favor asegúrese de que Flet esté instalado y en su PATH del sistema.")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"\n❌ ERROR FATAL: Build falló para {platform}.")
            print(f"Código de retorno: {e.returncode}")
            if e.stderr:
                print(f"\n--- Error Output ---")
                print(e.stderr)
            continue
        except Exception as e:
            print(f"\n❌ Error inesperado al construir {platform}: {e}")
            continue

    print(f"\n{'='*60}")
    print("🎉 PROCESO DE BUILD COMPLETADO! 🎉")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
