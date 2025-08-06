# path: build.py
import os
import subprocess
import sys


def main():
    """
    Script to build the TrackFit Flet application into an APK.

    This script verifies the project structure and then runs the
    `flet build apk` command with verbose output for debugging.
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"Project Root: {project_root}")

    # 1. Verify required project structure
    print("\n--- Verifying project structure ---")
    required_paths = {
        "Configuration file": os.path.join(project_root, "pyproject.toml"),
        "Source directory": os.path.join(project_root, "src"),
        "App entry point": os.path.join(project_root, "app.py"),
        "Source main entry point": os.path.join(project_root, "src", "main.py"),
        "Icon asset": os.path.join(project_root, "src", "assets", "app_icon.png"),
    }

    all_paths_ok = True
    for name, path in required_paths.items():
        if not os.path.exists(path):
            print(f"❌ ERROR: {name} not found at: {path}")
            all_paths_ok = False
        else:
            print(f"✅ OK: Found {name}.")

    if not all_paths_ok:
        print("\nPlease fix the missing files before building.")
        sys.exit(1)

    print("✅ Project structure is valid.")

    # 2. Construct and run the build command
    build_command = [
        "flet",
        "build",
        "windows",
        "-vv"  # Use verbose output for detailed logs
    ]

    print(f"\n--- Running build command: {' '.join(build_command)} ---")

    try:
        # Using subprocess.run to execute the command
        process = subprocess.run(
            build_command,
            cwd=project_root,
            check=True,
            text=True,
            encoding='utf-8'
        )
        print("\n--- Build Command Output ---")
        print(process.stdout)

    except FileNotFoundError:
        print("\n❌ FATAL ERROR: 'flet' command not found.")
        print("Please ensure Flet is installed and in your system's PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("\n❌ FATAL ERROR: Build process failed.")
        print(f"Return code: {e.returncode}")
        print("\n--- Error Output ---")
        print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        sys.exit(1)

    print("\n🎉 BUILD SUCCESSFUL! 🎉")
    print(f"Your Windows application can be found in: {os.path.join(project_root, 'build', 'windows')}")
    print(f"Executable: cortex_ai_agent.exe")


if __name__ == "__main__":
    main()