# -*- coding: utf-8 -*- # Added encoding declaration just in case
import flet as ft
import json
from pathlib import Path # Using pathlib for more modern path handling
import threading # Explicitly import for type hinting if needed
import os # Needed for os.walk in _map_project_thread

# --- Core Logic (separated for clarity) ---

# create_files_from_json_logic and _create_files_thread remain unchanged
# ... (copy the existing create_files_from_json_logic and _create_files_thread here) ...
def create_files_from_json_logic(base_dir, json_path, page: ft.Page, progress_ring: ft.ProgressRing, status_text: ft.Text, create_button: ft.ElevatedButton):
    """
    Reads a JSON file and creates files/directories based on its content.
    Updates UI elements for progress and status. Runs in a separate thread.
    Includes button state management.
    """
    try:
        create_button.disabled = True
        status_text.value = "Iniciando..."
        progress_ring.visible = True
        page.update()

        page.run_thread(
            _create_files_thread,
            base_dir,
            json_path,
            page,
            progress_ring,
            status_text,
            create_button  # Pass button to the thread
        )
    except Exception as e:
        show_dialog(page, "Error", f"Error starting thread: {e}")
        status_text.value = "Error al iniciar."
        progress_ring.visible = False
        create_button.disabled = False # Re-enable on error
        page.update()

def _create_files_thread(base_dir, json_path, page: ft.Page, progress_ring: ft.ProgressRing, status_text: ft.Text, create_button: ft.ElevatedButton):
    """Actual thread function for creating files. Manages button state."""
    try:
        base_dir_path = Path(base_dir)
        json_file_path = Path(json_path)

        if not base_dir_path.is_dir():
            show_dialog(page, "Error", "La ruta base seleccionada no es un directorio válido.")
            status_text.value = "Error: Ruta base inválida."
            return # Exit thread

        if not json_file_path.is_file():
            show_dialog(page, "Error", "El archivo JSON seleccionado no es válido.")
            status_text.value = "Error: Archivo JSON inválido."
            return # Exit thread

        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            show_dialog(page, "Error", f"No se pudo leer el archivo JSON: {e}")
            status_text.value = "Error leyendo JSON."
            return # Exit thread

        if not isinstance(data, list):
            show_dialog(page, "Error", "El contenido del JSON debe ser una lista de objetos.")
            status_text.value = "Error: JSON no es una lista."
            return # Exit thread

        total_items = len(data)
        processed_items = 0
        errors = []

        status_text.value = f"Procesando 0/{total_items}..." # Initial status
        page.update()

        for item in data:
            if not isinstance(item, dict) or "path" not in item or "content" not in item:
                errors.append("Un objeto en el JSON no tiene 'path' o 'content'. Se omitirá.")
                continue # Skip this item

            relative_path_str = item["path"]
            content = item["content"]

            try:
                full_path = base_dir_path.joinpath(relative_path_str).resolve()
                if base_dir_path.resolve() not in full_path.parents and full_path != base_dir_path.resolve():
                     errors.append(f"Intento de escritura fuera del directorio base: '{relative_path_str}'. Se omitirá.")
                     continue

                full_path.parent.mkdir(parents=True, exist_ok=True)

                with open(full_path, "w", encoding="utf-8") as archivo:
                    archivo.write(content)

                processed_items += 1
                status_text.value = f"Procesando: {processed_items}/{total_items} - {relative_path_str}"
                page.update()

            except OSError as e:
                 errors.append(f"Error de OS al procesar '{relative_path_str}': {e}")
            except Exception as e:
                errors.append(f"Error inesperado al procesar '{relative_path_str}': {e}")

        if not errors:
            status_text.value = f"¡Éxito! {processed_items} archivos creados correctamente."
            show_snackbar(page, "¡Archivos creados correctamente!")
        else:
            error_summary = f"Completado con {len(errors)} errores. {processed_items} archivos creados."
            status_text.value = error_summary
            error_details = "\n".join(errors[:10]) # Show first 10 errors
            if len(errors) > 10:
                error_details += f"\n... ({len(errors) - 10} errores más)"
            show_dialog(page, "Proceso completado con errores", error_details)

    except Exception as e:
        try:
            status_text.value = f"Error inesperado en el hilo: {e}"
            show_dialog(page, "Error Interno", f"Ocurrió un error inesperado en el proceso: {e}")
        except:
            print(f"Error grave en el hilo, no se pudo actualizar UI: {e}")

    finally:
        progress_ring.visible = False
        create_button.disabled = False
        page.update()


def map_project_logic(project_dir, extensions_to_include, extensions_to_exclude, output_file, page: ft.Page, progress_ring: ft.ProgressRing, status_text: ft.Text, map_button: ft.ElevatedButton):
    """
    Walks a project directory, finds files matching inclusion/exclusion criteria,
    and writes their content to a Markdown file.
    Updates UI elements for progress and status. Runs in a separate thread.
    Includes button state management.
    """
    try:
        map_button.disabled = True
        status_text.value = "Iniciando mapeo..."
        progress_ring.visible = True
        page.update()

        page.run_thread(
            _map_project_thread,
            project_dir,
            list(extensions_to_include),  # Ensure it's a list
            list(extensions_to_exclude), # Ensure it's a list
            output_file,
            page,
            progress_ring,
            status_text,
            map_button
        )
    except Exception as e:
        print(f"Error starting mapping thread: {e}")
        show_dialog(page, "Error", f"Error starting mapping thread: {e}")
        status_text.value = "Error al iniciar mapeo."
        progress_ring.visible = False
        map_button.disabled = False
        page.update()

def _map_project_thread(project_dir, extensions_to_include, extensions_to_exclude, output_file, page: ft.Page, progress_ring: ft.ProgressRing, status_text: ft.Text, map_button: ft.ElevatedButton):
    """Actual thread function for mapping project. Manages button state and exclusions."""
    try:
        project_path = Path(project_dir)
        output_path = Path(output_file)
        # Prepare sets for efficient lookup, case-insensitive
        include_extensions_set = set(ext.lower() for ext in extensions_to_include if ext.startswith('.'))
        # Exclusions are treated as simple strings to match the end of the filename
        exclude_patterns_set = set(excl.lower() for excl in extensions_to_exclude)

        if not project_path.is_dir():
            show_dialog(page, "Error", "La ruta del proyecto seleccionada no es un directorio válido.")
            status_text.value = "Error: Ruta de proyecto inválida."
            return

        if not include_extensions_set and not extensions_to_exclude:
             status_text.value = "Advertencia: No hay inclusiones ni exclusiones. Mapeando todos los archivos."
             page.update()
        elif not include_extensions_set:
             status_text.value = "Advertencia: No hay extensiones de inclusión. Mapeando archivos excepto los excluidos."
             page.update()


        found_files = 0
        try:
            with open(output_path, "w", encoding="utf-8") as out_f:
                out_f.write(f"# Mapeo del Proyecto: {project_path.name}\n\n")
                out_f.write(f"Directorio base: `{project_dir}`\n")
                out_f.write(f"Extensiones incluidas: `{', '.join(extensions_to_include) if extensions_to_include else 'Todas (excepto excluidas)'}`\n")
                out_f.write(f"Extensiones/Patrones excluidos: `{', '.join(extensions_to_exclude) if extensions_to_exclude else 'Ninguno'}`\n\n")
                out_f.write("---\n\n")

                status_text.value = "Recorriendo directorios..."
                page.update()

                for root, _, files in os.walk(project_dir):
                    current_dir_path = Path(root)
                    for filename in files:
                        # Check frequently if we should stop (Flet might handle page close)
                        # if not page.running: return

                        item_path = current_dir_path / filename
                        file_ext_lower = item_path.suffix.lower()
                        file_name_lower = item_path.name.lower()

                        # 1. Check inclusion criteria
                        # If include_extensions_set is empty, we potentially include everything.
                        # If it's not empty, the file extension MUST be in the set.
                        included_by_extension = not include_extensions_set or file_ext_lower in include_extensions_set

                        # 2. Check exclusion criteria
                        # If the file is potentially included, check if it matches any exclusion pattern.
                        is_excluded = False
                        if included_by_extension and exclude_patterns_set:
                            for excluded_pattern in exclude_patterns_set:
                                if file_name_lower.endswith(excluded_pattern):
                                    is_excluded = True
                                    break # Found an exclusion match

                        # 3. Final decision: Include if it met inclusion rules AND was NOT excluded
                        if included_by_extension and not is_excluded:
                            found_files += 1
                            relative_path = item_path.relative_to(project_path)
                            status_text.value = f"Mapeando ({found_files}): {relative_path}"
                            page.update()

                            out_f.write(f"## `{relative_path}`\n\n")
                            lang_hint = file_ext_lower.lstrip('.')
                            out_f.write(f"```{lang_hint}\n")
                            try:
                                with open(item_path, "r", encoding="utf-8", errors='ignore') as in_f:
                                    content = in_f.read()
                            except Exception as e:
                                content = f"Error al leer el archivo: {e}"
                            out_f.write(content)
                            out_f.write("\n```\n\n")


            status_text.value = f"¡Éxito! Mapeo completado. {found_files} archivos incluidos en '{output_file}'."
            show_snackbar(page, f"Archivo Markdown generado: {output_file}")

        except Exception as e:
            status_text.value = f"Error durante el mapeo: {e}"
            show_dialog(page, "Error de Mapeo", f"Ocurrió un error al generar el archivo Markdown: {e}")

    except Exception as e:
        try:
            status_text.value = f"Error inesperado en el hilo: {e}"
            show_dialog(page, "Error Interno", f"Ocurrió un error inesperado en el proceso: {e}")
        except:
             print(f"Error grave en el hilo de mapeo, no se pudo actualizar UI: {e}")

    finally:
        progress_ring.visible = False
        map_button.disabled = False
        page.update()


# --- UI Helper Functions ---

def show_dialog(page: ft.Page, title: str, message: str):
    """Displays a modal dialog."""
    try:
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message, selectable=True),
            actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(page, e.control.data))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        dlg.actions[0].data = dlg
        page.dialog = dlg
        dlg.open = True
        page.update()
    except Exception as e:
        print(f"Error showing dialog: {e}")

def close_dialog(page: ft.Page, dlg: ft.AlertDialog):
    """Closes the specified dialog."""
    try:
        if page.dialog == dlg:
            page.dialog.open = False
            page.update()
    except Exception as e:
        print(f"Error closing dialog: {e}")

def show_snackbar(page: ft.Page, message: str, error=False):
    """Displays a temporary SnackBar message."""
    try:
        sb = ft.SnackBar(
                ft.Text(message),
                open=True,
                bgcolor=ft.Colors.ERROR if error else ft.Colors.GREEN_700,
            )
        page.snack_bar = sb
        page.update()
    except Exception as e:
        print(f"Error showing snackbar: {e}")


# --- Flet Application ---

def main(page: ft.Page):
    page.title = "Utilidad de Archivos"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 850 # Increased width to accommodate side-by-side lists
    page.window_height = 700 # Increased height slightly

    # --- State Variables ---
    base_dir_path = ft.Ref[ft.Text]()
    json_file_path = ft.Ref[ft.Text]()
    project_dir_path = ft.Ref[ft.Text]()
    # Included extensions
    extensions_list = ft.Ref[ft.ListView]()
    new_extension_input = ft.Ref[ft.TextField]()
    # Excluded extensions
    excluded_extensions_list = ft.Ref[ft.ListView]()
    new_excluded_extension_input = ft.Ref[ft.TextField]()
    # Status indicators
    creator_status_text = ft.Ref[ft.Text]()
    creator_progress = ft.Ref[ft.ProgressRing]()
    mapper_status_text = ft.Ref[ft.Text]()
    mapper_progress = ft.Ref[ft.ProgressRing]()
    # Buttons to disable during processing
    create_button = ft.Ref[ft.ElevatedButton]()
    map_button = ft.Ref[ft.ElevatedButton]()

    # Python lists to hold extension strings
    current_extensions = []
    current_excluded_extensions = []

    # --- File Pickers ---
    def on_dialog_result(e: ft.FilePickerResultEvent):
        target_ref = e.page.overlay[e.page.overlay.index(e.control)].data
        target_text = target_ref.current
        if e.files:
             path = e.files[0].path
             target_text.value = path
             target_text.tooltip = path
        elif e.path:
            target_text.value = e.path
            target_text.tooltip = e.path
        else: # Handle cancellation
            if not target_text.value: # Only reset if nothing was selected before
                 target_text.value = target_text.data # Reset to initial text
                 target_text.tooltip = ""
        page.update()

    base_dir_picker = ft.FilePicker(on_result=on_dialog_result)
    base_dir_picker.data = base_dir_path
    json_file_picker = ft.FilePicker(on_result=on_dialog_result)
    json_file_picker.data = json_file_path
    project_dir_picker = ft.FilePicker(on_result=on_dialog_result)
    project_dir_picker.data = project_dir_path
    page.overlay.extend([base_dir_picker, json_file_picker, project_dir_picker])

    # --- Event Handlers ---

    # == Creator Tab Handlers ==
    def pick_base_dir(e):
        base_dir_picker.get_directory_path(dialog_title="Seleccionar directorio base")
        # Store initial text in control's data attribute for reset on cancel
        if base_dir_path.current: base_dir_path.current.data = base_dir_path.current.value


    def pick_json_file(e):
        # Store initial text in control's data attribute for reset on cancel
        if json_file_path.current: json_file_path.current.data = json_file_path.current.value
        json_file_picker.pick_files(dialog_title="Seleccionar archivo JSON", allow_multiple=False, allowed_extensions=["json"])


    def start_creation_process(e):
        base_dir = base_dir_path.current.value
        json_file = json_file_path.current.value

        if not base_dir or base_dir == "Ruta no seleccionada":
            show_dialog(page, "Error", "Debe seleccionar una ruta base.")
            return
        if not json_file or json_file == "JSON no seleccionado":
            show_dialog(page, "Error", "Debe seleccionar un archivo JSON.")
            return

        create_files_from_json_logic(
            base_dir,
            json_file,
            page,
            creator_progress.current,
            creator_status_text.current,
            create_button.current
        )

    # == Mapper Tab Handlers ==
    def pick_project_dir(e):
         # Store initial text in control's data attribute for reset on cancel
        if project_dir_path.current: project_dir_path.current.data = project_dir_path.current.value
        project_dir_picker.get_directory_path(dialog_title="Seleccionar carpeta del proyecto")

    # --- Included Extensions ---
    def add_extension(e):
        ext = new_extension_input.current.value.strip().lower()
        if not ext: return
        if not ext.startswith("."): ext = "." + ext # Force leading dot for inclusions
        if ext not in current_extensions:
            current_extensions.append(ext)
            update_extensions_view()
            new_extension_input.current.value = ""
            new_extension_input.current.focus()
            page.update()
        else:
            show_snackbar(page, f"La extensión de inclusión '{ext}' ya existe.", error=True)

    def delete_extension(e):
        ext_to_delete = e.control.data
        if ext_to_delete in current_extensions:
            current_extensions.remove(ext_to_delete)
            update_extensions_view()
            page.update()

    def update_extensions_view():
        controls = []
        for ext in sorted(current_extensions):
            controls.append(
                ft.Row(
                    [
                        ft.Text(ext, expand=True),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            tooltip=f"Eliminar inclusión {ext}",
                            on_click=delete_extension,
                            data=ext,
                            icon_color=ft.Colors.RED_400,
                            icon_size=18, # Slightly smaller icon
                            padding=ft.padding.only(left=0) # Reduce padding
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        if extensions_list.current:
            extensions_list.current.controls = controls

    # --- Excluded Extensions ---
    def add_excluded_extension(e):
        ext_excl = new_excluded_extension_input.current.value.strip().lower()
        if not ext_excl: return
        # No automatic dot prepending for exclusions
        if ext_excl not in current_excluded_extensions:
            current_excluded_extensions.append(ext_excl)
            update_excluded_extensions_view()
            new_excluded_extension_input.current.value = ""
            new_excluded_extension_input.current.focus()
            page.update()
        else:
            show_snackbar(page, f"La exclusión '{ext_excl}' ya existe.", error=True)

    def delete_excluded_extension(e):
        ext_to_delete = e.control.data
        if ext_to_delete in current_excluded_extensions:
            current_excluded_extensions.remove(ext_to_delete)
            update_excluded_extensions_view()
            page.update()

    def update_excluded_extensions_view():
        controls = []
        for ext in sorted(current_excluded_extensions):
            controls.append(
                ft.Row(
                    [
                        ft.Text(ext, expand=True),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            tooltip=f"Eliminar exclusión {ext}",
                            on_click=delete_excluded_extension,
                            data=ext,
                            icon_color=ft.Colors.RED_400,
                            icon_size=18, # Slightly smaller icon
                            padding=ft.padding.only(left=0) # Reduce padding
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        if excluded_extensions_list.current:
            excluded_extensions_list.current.controls = controls

    # --- Mapping Process Start ---
    def start_mapping_process(e):
        project_dir = project_dir_path.current.value
        output_dir = Path.cwd()
        output_file = output_dir / "salida_mapeo.md"

        if not project_dir or project_dir == "Ruta no seleccionada":
            show_dialog(page, "Error", "Debe seleccionar una carpeta de proyecto.")
            return

        # Confirmation for no included extensions is less critical now,
        # as it might be intended if exclusions are used.
        # We can remove the confirmation dialog or adjust its message.
        # Let's proceed without confirmation for now.

        _proceed_with_mapping(project_dir, str(output_file))


    def _proceed_with_mapping(project_dir, output_file):
        map_project_logic(
            project_dir,
            list(current_extensions),
            list(current_excluded_extensions), # Pass excluded list
            output_file,
            page,
            mapper_progress.current,
            mapper_status_text.current,
            map_button.current
        )


    # --- UI Layout ---

    # == Tab 1: Crear desde JSON ==
    tab_creator = ft.Container(
        padding=ft.padding.all(20),
        content=ft.Column(
            [
                ft.Text("Crear Estructura desde JSON", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Row([
                    ft.ElevatedButton("Seleccionar Ruta Base", icon=ft.Icons.FOLDER_OPEN, on_click=pick_base_dir),
                    ft.Text("Ruta no seleccionada", ref=base_dir_path, expand=True, no_wrap=True),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Row([
                    ft.ElevatedButton("Seleccionar Archivo JSON", icon=ft.Icons.UPLOAD_FILE, on_click=pick_json_file),
                    ft.Text("JSON no seleccionado", ref=json_file_path, expand=True, no_wrap=True),
                 ], alignment=ft.MainAxisAlignment.START),
                ft.Divider(height=20),
                ft.ElevatedButton(
                    "Crear Archivos",
                    ref=create_button,
                    icon=ft.Icons.CREATE_NEW_FOLDER,
                    on_click=start_creation_process,
                    bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE
                ),
                ft.Row([
                    ft.ProgressRing(ref=creator_progress, width=16, height=16, stroke_width=2, visible=False),
                    ft.Text("", ref=creator_status_text, expand=True, selectable=True)
                ], visible=True),
            ], spacing=15, scroll=ft.ScrollMode.ADAPTIVE,
        )
    )

    # == Tab 2: Mapear Proyecto ==
    tab_mapper = ft.Container(
        padding=ft.padding.all(20),
        content=ft.Column(
            [
                ft.Text("Mapear Proyecto a Markdown", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Row([
                    ft.ElevatedButton("Seleccionar Carpeta Proyecto", icon=ft.Icons.FOLDER_OPEN, on_click=pick_project_dir),
                    ft.Text("Ruta no seleccionada", ref=project_dir_path, expand=True, no_wrap=True),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Divider(height=10),

                # --- Row for Included and Excluded side-by-side ---
                ft.Row(
                    [
                        # --- Column for Included Extensions ---
                        ft.Column(
                            [
                                ft.Text("Extensiones a incluir (ej: .py, .dart):"),
                                ft.Row([
                                    ft.TextField(ref=new_extension_input, label="Incluir", hint_text=".ts", expand=True, dense=True, on_submit=add_extension),
                                    ft.ElevatedButton("Agregar", icon=ft.Icons.ADD, on_click=add_extension, tooltip="Añadir extensión a incluir"),
                                ], alignment=ft.MainAxisAlignment.START),
                                ft.Text("Incluidas:"),
                                ft.Container(
                                    content=ft.ListView(ref=extensions_list, spacing=2, auto_scroll=True),
                                    # height=180, # Adjust height as needed
                                    expand=True, # Take available vertical space
                                    border=ft.border.all(1, ft.Colors.with_opacity(0.5, ft.Colors.OUTLINE)),
                                    border_radius=ft.border_radius.all(4),
                                    padding=ft.padding.all(5),
                                ),
                            ],
                            expand=True, # Make this column take half the space
                            spacing=8,
                         ),

                        # --- Vertical Divider (Optional) ---
                        # ft.VerticalDivider(width=20),

                        # --- Column for Excluded Extensions ---
                        ft.Column(
                            [
                                ft.Text("Patrones a excluir (ej: .g.dart, _test.py):"),
                                ft.Row([
                                    ft.TextField(ref=new_excluded_extension_input, label="Excluir", hint_text=".g.dart", expand=True, dense=True, on_submit=add_excluded_extension),
                                    ft.ElevatedButton("Agregar", icon=ft.Icons.ADD, on_click=add_excluded_extension, tooltip="Añadir patrón a excluir"),
                                ], alignment=ft.MainAxisAlignment.START),
                                ft.Text("Excluidas:"),
                                ft.Container(
                                    content=ft.ListView(ref=excluded_extensions_list, spacing=2, auto_scroll=True),
                                    # height=180, # Adjust height as needed
                                    expand=True, # Take available vertical space
                                    border=ft.border.all(1, ft.Colors.with_opacity(0.5, ft.Colors.OUTLINE)),
                                    border_radius=ft.border_radius.all(4),
                                    padding=ft.padding.all(5),
                                ),
                            ],
                            expand=True, # Make this column take half the space
                            spacing=8,
                         ),
                    ],
                    spacing=15, # Space between the two columns
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    # Give the row a fixed height or let it expand based on content + expanded containers
                    height=280 # Adjust overall height for the extension area
                ),
                # --- End of Row for Extensions ---

                ft.Divider(height=20),
                 ft.ElevatedButton(
                    "Iniciar Mapeo",
                    ref=map_button,
                    icon=ft.Icons.DOCUMENT_SCANNER,
                    on_click=start_mapping_process,
                    bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE
                 ),
                 ft.Row([
                    ft.ProgressRing(ref=mapper_progress, width=16, height=16, stroke_width=2, visible=False),
                    ft.Text("", ref=mapper_status_text, expand=True, selectable=True)
                 ], visible=True),
                 ft.Text("Salida: 'salida_mapeo.md' en el directorio actual.", italic=True, size=11, selectable=True)

            ], spacing=10, # Adjusted spacing for tighter layout
               scroll=ft.ScrollMode.ADAPTIVE,
        )
    )

    # --- Main Tabs Control ---
    tabs = ft.Tabs(
        selected_index=0, animation_duration=300,
        tabs=[
            ft.Tab(text="Crear desde JSON", content=tab_creator, icon=ft.Icons.SOURCE),
            ft.Tab(text="Mapear Proyecto", content=tab_mapper, icon=ft.Icons.MAP),
        ], expand=True,
    )

    page.add(tabs)
    # Initial setup for both lists
    if base_dir_path.current: base_dir_path.current.data = base_dir_path.current.value
    if json_file_path.current: json_file_path.current.data = json_file_path.current.value
    if project_dir_path.current: project_dir_path.current.data = project_dir_path.current.value
    update_extensions_view()
    update_excluded_extensions_view() # Initialize excluded list view
    page.update()

# --- Run the App ---
if __name__ == "__main__":
    ft.app(target=main)