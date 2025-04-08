# -*- coding: utf-8 -*- # Added encoding declaration just in case
import flet as ft
import json
from pathlib import Path # Using pathlib for more modern path handling
import threading # Explicitly import for type hinting if needed

# --- Core Logic (separated for clarity) ---

# ... (create_files_from_json_logic and _create_files_thread remain the same) ...
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

        # Update UI: Show progress (already done before thread start)
        # status_text.value = "Procesando JSON..."
        # progress_ring.visible = True
        # page.update() # Avoid redundant update

        if not base_dir_path.is_dir():
            show_dialog(page, "Error", "La ruta base seleccionada no es un directorio válido.")
            status_text.value = "Error: Ruta base inválida."
            # progress_ring.visible = False # Handled in finally
            # page.update() # Handled in finally
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
            # Check frequently if we should stop (e.g., page closed - Flet might handle this)
            # if not page.running: return # Example check

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
                # Check if the resolved path is within the base directory
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

    except Exception as e:
        # Catch any unexpected error within the thread itself
        try:
            status_text.value = f"Error inesperado en el hilo: {e}"
            show_dialog(page, "Error Interno", f"Ocurrió un error inesperado en el proceso: {e}")
        except:
            print(f"Error grave en el hilo, no se pudo actualizar UI: {e}") # Fallback print

    finally:
        # Ensure UI elements are reset correctly, regardless of errors
        progress_ring.visible = False
        create_button.disabled = False
        page.update()


def map_project_logic(project_dir, extensions, output_file, page: ft.Page, progress_ring: ft.ProgressRing, status_text: ft.Text, map_button: ft.ElevatedButton):
    """
    Walks a project directory, finds files with specified extensions,
    and writes their content to a Markdown file.
    Updates UI elements for progress and status. Runs in a separate thread.
    Includes button state management.
    """
    try:
        # Disable button, show progress before starting thread
        map_button.disabled = True
        status_text.value = "Iniciando mapeo..."
        progress_ring.visible = True
        page.update()

        page.run_thread(
            _map_project_thread,
            project_dir,
            list(extensions),
            output_file,
            page,
            progress_ring,
            status_text,
            map_button  # Pass button to the thread
        )
    except Exception as e:
        print(f"Error starting mapping thread: {e}")  # Keep print for debugging
        show_dialog(page, "Error", f"Error starting mapping thread: {e}")
        status_text.value = "Error al iniciar mapeo."
        progress_ring.visible = False
        map_button.disabled = False # Re-enable on error
        page.update()

def _map_project_thread(project_dir, extensions, output_file, page: ft.Page, progress_ring: ft.ProgressRing, status_text: ft.Text, map_button: ft.ElevatedButton):
    """Actual thread function for mapping project. Manages button state."""
    try:
        project_path = Path(project_dir)
        output_path = Path(output_file)
        extensions_set = set(ext.lower() for ext in extensions) # Lowercase for case-insensitive compare

        # Update UI: Show progress (already done before thread start)
        # status_text.value = "Iniciando mapeo..."
        # progress_ring.visible = True
        # page.update() # Avoid redundant update

        if not project_path.is_dir():
            show_dialog(page, "Error", "La ruta del proyecto seleccionada no es un directorio válido.")
            status_text.value = "Error: Ruta de proyecto inválida."
            # progress_ring.visible = False # Handled in finally
            # page.update() # Handled in finally
            return # Exit thread

        if not extensions_set:
            # No need for a dialog here, just write the header
             status_text.value = "Advertencia: No hay extensiones. Generando archivo vacío."
             page.update()
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
                all_files_gen = project_path.rglob("*") # Use generator for potentially large dirs

                for item_path in all_files_gen:
                    # Check frequently if we should stop
                    # if not page.running: return

                    if item_path.is_file():
                        file_ext = item_path.suffix.lower()
                        if file_ext in extensions_set:
                            found_files += 1
                            relative_path = item_path.relative_to(project_path)
                            status_text.value = f"Mapeando ({found_files}): {relative_path}"
                            page.update()

                            out_f.write(f"## `{relative_path}`\n\n")
                            # Determine language hint for markdown code block
                            lang_hint = file_ext.lstrip('.')
                            out_f.write(f"```{lang_hint}\n")
                            try:
                                # Add better error handling for file reading (e.g., binary files)
                                with open(item_path, "r", encoding="utf-8", errors='ignore') as in_f:
                                    content = in_f.read()
                            except Exception as e:
                                content = f"Error al leer el archivo: {e}"
                            out_f.write(content)
                            out_f.write("\n```\n\n")

            # Final status update after loop finishes
            status_text.value = f"¡Éxito! Mapeo completado. {found_files} archivos incluidos en '{output_file}'."
            show_snackbar(page, f"Archivo Markdown generado: {output_file}") # Corrected call below

        except Exception as e:
            # Error during file writing or iteration
            status_text.value = f"Error durante el mapeo: {e}"
            show_dialog(page, "Error de Mapeo", f"Ocurrió un error al generar el archivo Markdown: {e}")

    except Exception as e:
        # Catch any unexpected error within the thread itself
        try:
            status_text.value = f"Error inesperado en el hilo: {e}"
            show_dialog(page, "Error Interno", f"Ocurrió un error inesperado en el proceso: {e}")
        except:
             print(f"Error grave en el hilo de mapeo, no se pudo actualizar UI: {e}") # Fallback print

    finally:
        # Ensure UI elements are reset correctly, regardless of errors
        progress_ring.visible = False
        map_button.disabled = False
        page.update()

# --- UI Helper Functions ---

def show_dialog(page: ft.Page, title: str, message: str):
    """Displays a modal dialog."""
    # CORRECTED: Directly assign the new dialog. Flet handles replacement.
    # The 'page' object passed here *should* be the main page object.
    try:
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message, selectable=True), # Make content selectable
            actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(page, e.control.data))], # Pass dialog instance for closing
            actions_alignment=ft.MainAxisAlignment.END,
        )
        # Pass the dialog instance itself to the close button's data
        dlg.actions[0].data = dlg
        page.dialog = dlg # Assign to page attribute
        dlg.open = True
        page.update()
    except Exception as e:
        print(f"Error showing dialog: {e}") # Fallback for critical errors

def close_dialog(page: ft.Page, dlg: ft.AlertDialog):
    """Closes the specified dialog."""
    # Check if the dialog we want to close is the currently assigned one
    try:
        if page.dialog == dlg:
            page.dialog.open = False
            page.update() # Update needed to reflect closure
            # It's generally safer NOT to set page.dialog = None here,
            # let Flet manage the attribute lifecycle.
    except Exception as e:
        print(f"Error closing dialog: {e}")

def show_snackbar(page: ft.Page, message: str, error=False):
    """Displays a temporary SnackBar message."""
    # CORRECTED: Assign to page.snack_bar and open it
    try:
        sb = ft.SnackBar(
                ft.Text(message),
                open=True,
                bgcolor=ft.Colors.ERROR if error else ft.Colors.GREEN_700,
            )
        page.snack_bar = sb # Assign the instance
        page.update() # Update the page to show the snackbar
    except Exception as e:
        print(f"Error showing snackbar: {e}")


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
    # Keep the FilePicker setup as it was in the previous corrected version
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

    def pick_json_file(e):
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

        # Logic now handles button disabling/enabling and status updates
        create_files_from_json_logic(
            base_dir,
            json_file,
            page,
            creator_progress.current,
            creator_status_text.current,
            create_button.current # Pass the button control
        )

    # == Mapper Tab Handlers ==
    def pick_project_dir(e):
        project_dir_picker.get_directory_path(dialog_title="Seleccionar carpeta del proyecto")

    def add_extension(e):
        ext = new_extension_input.current.value.strip().lower()
        if not ext: return
        if not ext.startswith("."): ext = "." + ext
        if ext not in current_extensions:
            current_extensions.append(ext)
            update_extensions_view()
            new_extension_input.current.value = ""
            new_extension_input.current.focus()
            page.update()
        else:
            show_snackbar(page, f"La extensión '{ext}' ya existe.", error=True)

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
                            tooltip=f"Eliminar {ext}",
                            on_click=delete_extension,
                            data=ext,
                            icon_color=ft.Colors.RED_400,
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
        if extensions_list.current:
            extensions_list.current.controls = controls

    def start_mapping_process(e):
        project_dir = project_dir_path.current.value
        output_dir = Path.cwd()
        output_file = output_dir / "salida_mapeo.md"

        if not project_dir or project_dir == "Ruta no seleccionada":
            show_dialog(page, "Error", "Debe seleccionar una carpeta de proyecto.")
            return

        def on_confirm_no_ext(evt):
            local_page = evt.page
            dlg_to_close = local_page.dialog
            if dlg_to_close:
                close_dialog(local_page, dlg_to_close)
            if evt.control.data == "yes":
                _proceed_with_mapping(project_dir, str(output_file))

        if not current_extensions:
            dlg_confirm = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmar Mapeo"),
                content=ft.Text("No se ha agregado ninguna extensión. ¿Continuar y generar un archivo vacío?"),
                actions=[
                    ft.TextButton("Sí", on_click=on_confirm_no_ext, data="yes"),
                    ft.TextButton("No", on_click=lambda evt: close_dialog(evt.page, evt.page.dialog) , data="no"),
                ], actions_alignment=ft.MainAxisAlignment.END
            )
            # Pass the dialog instance to the 'No' button's close action
            dlg_confirm.actions[1].on_click = lambda evt: close_dialog(evt.page, dlg_confirm)

            page.dialog = dlg_confirm
            dlg_confirm.open = True
            page.update()
            return

        _proceed_with_mapping(project_dir, str(output_file))

    def _proceed_with_mapping(project_dir, output_file):
        # Logic now handles button disabling/enabling and status updates
        map_project_logic(
            project_dir,
            list(current_extensions),
            output_file,
            page,
            mapper_progress.current,
            mapper_status_text.current,
            map_button.current # Pass the button control
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
                    ref=create_button, # Ref for the button itself
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
                ft.Text("Extensiones a incluir (ej: .py, .js, .css):"),
                ft.Row([
                    ft.TextField(ref=new_extension_input, label="Nueva extensión", hint_text=".ts", expand=True, dense=True, on_submit=add_extension),
                    ft.ElevatedButton("Agregar", icon=ft.Icons.ADD, on_click=add_extension),
                ]),
                ft.Text("Extensiones agregadas:"),
                ft.Container(
                    content=ft.ListView(ref=extensions_list, spacing=5, auto_scroll=True),
                    height=150,
                    # CORRECTED: Use ft.Colors.OUTLINE
                    border=ft.border.all(1, ft.Colors.OUTLINE), # Use theme color
                    border_radius=ft.border_radius.all(4),
                    padding=ft.padding.all(5),
                ),
                ft.Divider(height=20),
                 ft.ElevatedButton(
                    "Iniciar Mapeo",
                    ref=map_button, # Ref for the button itself
                    icon=ft.Icons.DOCUMENT_SCANNER,
                    on_click=start_mapping_process,
                    bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE
                 ),
                 ft.Row([
                    ft.ProgressRing(ref=mapper_progress, width=16, height=16, stroke_width=2, visible=False),
                    ft.Text("", ref=mapper_status_text, expand=True, selectable=True)
                 ], visible=True),
                 ft.Text("Salida: 'salida_mapeo.md' en el directorio actual.", italic=True, size=11, selectable=True)

            ], spacing=15, scroll=ft.ScrollMode.ADAPTIVE,
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
    update_extensions_view()
    page.update()

# --- Run the App ---
if __name__ == "__main__":
    ft.app(target=main)