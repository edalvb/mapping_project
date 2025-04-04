import flet as ft
import json
from pathlib import Path # Using pathlib for more modern path handling

# --- Core Logic (separated for clarity) ---

def create_files_from_json_logic(base_dir, json_path, page: ft.Page, progress_ring: ft.ProgressRing, status_text: ft.Text):
    """
    Reads a JSON file and creates files/directories based on its content.
    Updates UI elements for progress and status. Runs in a separate thread.
    """
    try:
        page.run_thread(
            target=_create_files_thread,
            args=(base_dir, json_path, page, progress_ring, status_text)
        )
    except Exception as e:
        show_dialog(page, "Error", f"Error starting thread: {e}")
        status_text.value = "Error al iniciar."
        progress_ring.visible = False
        page.update()

def _create_files_thread(base_dir, json_path, page: ft.Page, progress_ring: ft.ProgressRing, status_text: ft.Text):
    """Actual thread function for creating files."""
    base_dir_path = Path(base_dir)
    json_file_path = Path(json_path)

    # Update UI: Show progress
    status_text.value = "Procesando JSON..."
    progress_ring.visible = True
    page.update()

    if not base_dir_path.is_dir():
        show_dialog(page, "Error", "La ruta base seleccionada no es un directorio válido.")
        status_text.value = "Error: Ruta base inválida."
        progress_ring.visible = False
        page.update()
        return

    if not json_file_path.is_file():
        show_dialog(page, "Error", "El archivo JSON seleccionado no es válido.")
        status_text.value = "Error: Archivo JSON inválido."
        progress_ring.visible = False
        page.update()
        return

    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        show_dialog(page, "Error", f"No se pudo leer el archivo JSON: {e}")
        status_text.value = "Error leyendo JSON."
        progress_ring.visible = False
        page.update()
        return

    if not isinstance(data, list):
        show_dialog(page, "Error", "El contenido del JSON debe ser una lista de objetos.")
        status_text.value = "Error: JSON no es una lista."
        progress_ring.visible = False
        page.update()
        return

    total_items = len(data)
    processed_items = 0
    errors = []

    for item in data:
        if not isinstance(item, dict) or "path" not in item or "content" not in item:
            errors.append("Un objeto en el JSON no tiene 'path' o 'content'. Se omitirá.")
            continue # Skip this item

        relative_path_str = item["path"]
        content = item["content"]

        # Construct the full path using pathlib
        try:
            # Ensure the path is treated as relative to the base directory
            # Prevent escaping the base directory (basic security)
            full_path = base_dir_path.joinpath(relative_path_str).resolve()
            if base_dir_path.resolve() not in full_path.parents and full_path != base_dir_path.resolve():
                 errors.append(f"Intento de escritura fuera del directorio base: '{relative_path_str}'. Se omitirá.")
                 continue

            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the file content
            with open(full_path, "w", encoding="utf-8") as archivo:
                archivo.write(content)

            processed_items += 1
            status_text.value = f"Procesando: {processed_items}/{total_items} - {relative_path_str}"
            page.update()

        except OSError as e:
             errors.append(f"Error de OS al procesar '{relative_path_str}': {e}")
        except Exception as e:
            errors.append(f"Error inesperado al procesar '{relative_path_str}': {e}")


    # Final status update
    progress_ring.visible = False
    if not errors:
        status_text.value = f"¡Éxito! {processed_items} archivos creados correctamente."
        show_snackbar(page, "¡Archivos creados correctamente!")
    else:
        error_summary = f"Completado con {len(errors)} errores. {processed_items} archivos creados."
        status_text.value = error_summary
        # Combine errors for dialog display, limit length if necessary
        error_details = "\n".join(errors[:10]) # Show first 10 errors
        if len(errors) > 10:
            error_details += f"\n... ({len(errors) - 10} errores más)"
        show_dialog(page, "Proceso completado con errores", error_details)

    page.update()


def map_project_logic(project_dir, extensions, output_file, page: ft.Page, progress_ring: ft.ProgressRing, status_text: ft.Text):
    """
    Walks a project directory, finds files with specified extensions,
    and writes their content to a Markdown file.
    Updates UI elements for progress and status. Runs in a separate thread.
    """
    try:
        page.run_thread(
            target=_map_project_thread,
            args=(project_dir, extensions, output_file, page, progress_ring, status_text)

        )
    except Exception as e:
        show_dialog(page, "Error", f"Error starting mapping thread: {e}")
        status_text.value = "Error al iniciar mapeo."
        progress_ring.visible = False
        page.update()

def _map_project_thread(project_dir, extensions, output_file, page: ft.Page, progress_ring: ft.ProgressRing, status_text: ft.Text):
    """Actual thread function for mapping project."""
    project_path = Path(project_dir)
    output_path = Path(output_file)
    extensions_set = set(ext.lower() for ext in extensions) # Lowercase for case-insensitive compare

    # Update UI: Show progress
    status_text.value = "Iniciando mapeo..."
    progress_ring.visible = True
    page.update()

    if not project_path.is_dir():
        show_dialog(page, "Error", "La ruta del proyecto seleccionada no es un directorio válido.")
        status_text.value = "Error: Ruta de proyecto inválida."
        progress_ring.visible = False
        page.update()
        return

    if not extensions_set:
        show_dialog(page, "Advertencia", "No se seleccionaron extensiones. El archivo de salida estará vacío.")
        # Allow continuing, might be intentional

    found_files = 0
    try:
        with open(output_path, "w", encoding="utf-8") as out_f:
            out_f.write(f"# Mapeo del Proyecto: {project_path.name}\n\n")
            out_f.write(f"Directorio base: `{project_dir}`\n")
            out_f.write(f"Extensiones incluidas: `{', '.join(extensions) if extensions else 'Ninguna'}`\n\n")
            out_f.write("---\n\n")

            status_text.value = "Recorriendo directorios..."
            page.update()

            # Using pathlib's rglob for potentially cleaner iteration
            all_files = list(project_path.rglob("*.*")) # Get all files first for progress indication
            total_files_to_check = len(all_files)
            checked_files = 0

            for file_path in all_files:
                 checked_files += 1
                 if file_path.is_file():
                     # status_text.value = f"Verificando {checked_files}/{total_files_to_check}: {file_path.name}"
                     # page.update() # Updating too often can slow things down

                     file_ext = file_path.suffix.lower()
                     if file_ext in extensions_set:
                         found_files += 1
                         status_text.value = f"Mapeando: {file_path.relative_to(project_path)}"
                         page.update()

                         relative_path = file_path.relative_to(project_path)
                         out_f.write(f"## `{relative_path}`\n\n")
                         # Determine language hint for markdown code block
                         lang_hint = file_ext.lstrip('.')
                         out_f.write(f"```{lang_hint}\n")
                         try:
                             with open(file_path, "r", encoding="utf-8") as in_f:
                                 content = in_f.read()
                         except Exception as e:
                             content = f"Error al leer el archivo: {e}"
                         out_f.write(content)
                         out_f.write("\n```\n\n")

        # Final status update
        status_text.value = f"¡Éxito! Mapeo completado. {found_files} archivos incluidos en '{output_file}'."
        show_snackbar(page, f"Archivo Markdown generado: {output_file}")

    except Exception as e:
        status_text.value = f"Error durante el mapeo: {e}"
        show_dialog(page, "Error de Mapeo", f"Ocurrió un error al generar el archivo Markdown: {e}")

    finally:
        progress_ring.visible = False
        page.update()

# --- UI Helper Functions ---

def show_dialog(page: ft.Page, title: str, message: str):
    """Displays a modal dialog."""
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(page, dlg))],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

def close_dialog(page: ft.Page, dlg: ft.AlertDialog):
    """Closes the currently open dialog."""
    page.dialog.open = False
    page.update()

def show_snackbar(page: ft.Page, message: str, error=False):
    """Displays a temporary SnackBar message."""
    page.snack_bar = ft.SnackBar(
            ft.Text(message),
            open=True,
            bgcolor=ft.colors.ERROR if error else ft.colors.GREEN_700,
        )
    page.update()

# --- Flet Application ---

def main(page: ft.Page):
    page.title = "Utilidad de Archivos"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 700
    page.window_height = 650

    # --- State Variables ---
    base_dir_path = ft.Ref[ft.Text]()
    json_file_path = ft.Ref[ft.Text]()
    project_dir_path = ft.Ref[ft.Text]()
    extensions_list = ft.Ref[ft.ListView]()
    new_extension_input = ft.Ref[ft.TextField]()
    # Status indicators
    creator_status_text = ft.Ref[ft.Text]()
    creator_progress = ft.Ref[ft.ProgressRing]()
    mapper_status_text = ft.Ref[ft.Text]()
    mapper_progress = ft.Ref[ft.ProgressRing]()
    # Buttons to disable during processing
    create_button = ft.Ref[ft.ElevatedButton]()
    map_button = ft.Ref[ft.ElevatedButton]()


    current_extensions = [] # Python list to hold extension strings

    # --- File Pickers ---
    def on_dialog_result(e: ft.FilePickerResultEvent):
        target_ref = e.control.data # Get the target Text control reference
        target_text = target_ref.current

        if e.path:
            target_text.value = e.path
            target_text.tooltip = e.path # Show full path on hover
        else:
            # Keep existing value if user cancelled
            # target_text.value = "Selección cancelada"
            pass
        page.update()

    # Separate pickers for clarity, linked via 'data' attribute
    base_dir_picker = ft.FilePicker(on_result=on_dialog_result, data=base_dir_path)
    json_file_picker = ft.FilePicker(on_result=on_dialog_result, data=json_file_path)
    project_dir_picker = ft.FilePicker(on_result=on_dialog_result, data=project_dir_path)

    # Add pickers to overlay (required by Flet)
    page.overlay.extend([base_dir_picker, json_file_picker, project_dir_picker])

    # --- Event Handlers ---

    # == Creator Tab Handlers ==
    def pick_base_dir(e):
        base_dir_picker.get_directory_path(
            dialog_title="Seleccionar directorio base",
        )

    def pick_json_file(e):
        json_file_picker.pick_files(
            dialog_title="Seleccionar archivo JSON",
            allow_multiple=False,
            allowed_extensions=["json"]
        )

    def start_creation_process(e):
        base_dir = base_dir_path.current.value
        json_file = json_file_path.current.value

        if not base_dir or base_dir == "Ruta no seleccionada":
            show_dialog(page, "Error", "Debe seleccionar una ruta base.")
            return
        if not json_file or json_file == "JSON no seleccionado":
            show_dialog(page, "Error", "Debe seleccionar un archivo JSON.")
            return

        # Disable button, show progress
        create_button.current.disabled = True
        creator_status_text.current.value = "Iniciando..."
        creator_progress.current.visible = True
        page.update()

        # Run the logic (which handles threading)
        create_files_from_json_logic(
            base_dir,
            json_file,
            page,
            creator_progress.current,
            creator_status_text.current
        )
        # Re-enable button immediately - thread handles status
        create_button.current.disabled = False
        page.update()


    # == Mapper Tab Handlers ==
    def pick_project_dir(e):
        project_dir_picker.get_directory_path(
            dialog_title="Seleccionar carpeta del proyecto",
        )

    def add_extension(e):
        ext = new_extension_input.current.value.strip().lower()
        if not ext:
            return

        # Ensure it starts with a dot
        if not ext.startswith("."):
            ext = "." + ext

        if ext not in current_extensions:
            current_extensions.append(ext)
            update_extensions_view()
            new_extension_input.current.value = "" # Clear input
            new_extension_input.current.focus() # Keep focus
            page.update()
        else:
             show_snackbar(page, f"La extensión '{ext}' ya existe.", error=True)


    def delete_extension(e):
        ext_to_delete = e.control.data # Get extension from button data
        if ext_to_delete in current_extensions:
            current_extensions.remove(ext_to_delete)
            update_extensions_view()
            page.update()

    def update_extensions_view():
        """Rebuilds the ListView for extensions."""
        controls = []
        for ext in sorted(current_extensions): # Sort for consistent display
            controls.append(
                ft.Row(
                    [
                        ft.Text(ext, expand=True),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip=f"Eliminar {ext}",
                            on_click=delete_extension,
                            data=ext, # Pass the extension to delete
                            icon_color=ft.colors.RED_400,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
        extensions_list.current.controls = controls

    def start_mapping_process(e):
        project_dir = project_dir_path.current.value
        output_file = "salida_mapeo.md" # Fixed output filename

        if not project_dir or project_dir == "Ruta no seleccionada":
            show_dialog(page, "Error", "Debe seleccionar una carpeta de proyecto.")
            return
        if not current_extensions:
            # Ask for confirmation if no extensions are added
            def on_confirm_no_ext(evt):
                close_dialog(page, dlg_confirm)
                if evt.control.data == "yes":
                     _proceed_with_mapping(project_dir, output_file)

            dlg_confirm = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmar Mapeo"),
                content=ft.Text("No se ha agregado ninguna extensión. ¿Desea continuar y generar un archivo con encabezado pero sin contenido de archivos?"),
                actions=[
                    ft.TextButton("Sí", on_click=on_confirm_no_ext, data="yes"),
                    ft.TextButton("No", on_click=lambda evt: close_dialog(page, dlg_confirm), data="no"),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.dialog = dlg_confirm
            dlg_confirm.open = True
            page.update()
            return # Wait for dialog confirmation

        # Proceed directly if extensions exist
        _proceed_with_mapping(project_dir, output_file)

    def _proceed_with_mapping(project_dir, output_file):
        # Disable button, show progress
        map_button.current.disabled = True
        mapper_status_text.current.value = "Iniciando mapeo..."
        mapper_progress.current.visible = True
        page.update()

        # Run the logic (which handles threading)
        map_project_logic(
            project_dir,
            list(current_extensions), # Pass a copy
            output_file,
            page,
            mapper_progress.current,
            mapper_status_text.current
        )

        # Re-enable button immediately
        map_button.current.disabled = False
        page.update()


    # --- UI Layout ---

    # == Tab 1: Crear desde JSON ==
    tab_creator = ft.Container(
        padding=ft.padding.all(20),
        content=ft.Column(
            [
                ft.Text("Crear Estructura desde JSON", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Row(
                    [
                        ft.ElevatedButton("Seleccionar Ruta Base", icon=ft.icons.FOLDER_OPEN, on_click=pick_base_dir),
                        ft.Text("Ruta no seleccionada", ref=base_dir_path, expand=True, no_wrap=True),
                    ],
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Row(
                     [
                        ft.ElevatedButton("Seleccionar Archivo JSON", icon=ft.icons.UPLOAD_FILE, on_click=pick_json_file),
                        ft.Text("JSON no seleccionado", ref=json_file_path, expand=True, no_wrap=True),
                     ],
                     alignment=ft.MainAxisAlignment.START
                ),
                ft.Divider(height=20),
                ft.ElevatedButton(
                    "Crear Archivos",
                    ref=create_button,
                    icon=ft.icons.CREATE_NEW_FOLDER,
                    on_click=start_creation_process,
                    bgcolor=ft.colors.GREEN_700,
                    color=ft.colors.WHITE
                ),
                ft.Row(
                    [
                        ft.ProgressRing(ref=creator_progress, width=16, height=16, stroke_width=2, visible=False),
                        ft.Text("", ref=creator_status_text, expand=True) # Status message area
                    ],
                    visible=True # Initially visible, progress ring toggles
                ),
            ],
            spacing=15
        )
    )

    # == Tab 2: Mapear Proyecto ==
    tab_mapper = ft.Container(
        padding=ft.padding.all(20),
        content=ft.Column(
            [
                ft.Text("Mapear Proyecto a Markdown", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Row(
                    [
                        ft.ElevatedButton("Seleccionar Carpeta Proyecto", icon=ft.icons.FOLDER_OPEN, on_click=pick_project_dir),
                        ft.Text("Ruta no seleccionada", ref=project_dir_path, expand=True, no_wrap=True),
                    ],
                     alignment=ft.MainAxisAlignment.START
                ),
                ft.Divider(height=10),
                ft.Text("Extensiones a incluir (ej: .py, .js, .css):"),
                ft.Row(
                    [
                        ft.TextField(
                            ref=new_extension_input,
                            label="Nueva extensión",
                            hint_text=".ts",
                            expand=True,
                            dense=True,
                            on_submit=add_extension # Allow adding by pressing Enter
                        ),
                        ft.ElevatedButton("Agregar", icon=ft.icons.ADD, on_click=add_extension),
                    ]
                ),
                ft.Text("Extensiones agregadas:"),
                ft.ListView(ref=extensions_list, height=150, spacing=5, auto_scroll=True),
                ft.Divider(height=20),
                 ft.ElevatedButton(
                    "Iniciar Mapeo",
                    ref=map_button,
                    icon=ft.icons.DOCUMENT_SCANNER,
                    on_click=start_mapping_process,
                    bgcolor=ft.colors.BLUE_700,
                    color=ft.colors.WHITE
                 ),
                 ft.Row(
                    [
                        ft.ProgressRing(ref=mapper_progress, width=16, height=16, stroke_width=2, visible=False),
                        ft.Text("", ref=mapper_status_text, expand=True) # Status message area
                    ],
                     visible=True
                 ),
                 ft.Text("El archivo de salida se guardará como 'salida_mapeo.md' en el directorio actual.", italic=True, size=11)

            ],
            spacing=15
        )
    )

    # --- Main Tabs Control ---
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Crear desde JSON", content=tab_creator, icon=ft.icons.SOURCE),
            ft.Tab(text="Mapear Proyecto", content=tab_mapper, icon=ft.icons.MAP),
        ],
        expand=True,
    )

    page.add(tabs)
    update_extensions_view() # Initial population of the (empty) list view
    page.update()


# --- Run the App ---
if __name__ == "__main__":
    ft.app(target=main)