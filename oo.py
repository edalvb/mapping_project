import os
import json
import tkinter as tk
from tkinter import (
    filedialog, simpledialog, messagebox,
    Toplevel, StringVar, BooleanVar, Checkbutton, ttk
)
from dotenv import load_dotenv

# Usa la librería google.genai
from google import genai
from google.genai import types

# Carga las variables de entorno (por ejemplo, GEMINI_API_KEY).
load_dotenv()


###############################################################################
#                           Funciones Auxiliares
###############################################################################

def listar_archivos_directorio(path):
    """
    Retorna en dos listas separadas: los archivos y las carpetas del primer nivel en 'path'.
    No profundiza en subdirectorios, ni archivos dentro de carpetas.
    """
    if not os.path.isdir(path):
        return [], []
    items = os.listdir(path)
    archivos = []
    carpetas = []
    for item in items:
        full_path = os.path.join(path, item)
        if os.path.isfile(full_path):
            archivos.append(item)
        elif os.path.isdir(full_path):
            carpetas.append(item)
    return archivos, carpetas


def listar_archivos_subcarpetas(path, extensiones=None):
    """
    Retorna una lista (absoluta) de archivos (recorriendo recursivamente el directorio).
    Si 'extensiones' no es None, filtra solo los que coincidan con dichas extensiones.
    """
    archivos_encontrados = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if extensiones:
                ext_actual = os.path.splitext(file)[1].lower()
                if ext_actual not in extensiones:
                    continue
            archivos_encontrados.append(os.path.join(root, file))
    return archivos_encontrados


def obtener_markdown_de_archivos(lista_rutas_archivos, raiz_base):
    """
    Genera un string de Markdown con el contenido de los archivos dados en 'lista_rutas_archivos'.
    'raiz_base' se usa para calcular la ruta relativa dentro del texto.
    """
    markdown = "# Mapeo de Archivos del Proyecto\n\n"
    for ruta_completa in lista_rutas_archivos:
        ruta_relativa = os.path.relpath(ruta_completa, raiz_base)
        markdown += f"## {ruta_relativa}\n\n"
        markdown += "```plaintext\n"
        contenido = ""
        try:
            with open(ruta_completa, "r", encoding="utf-8") as f:
                contenido = f.read()
        except Exception as e:
            contenido = f"Error al leer el archivo: {e}"
        markdown += contenido
        markdown += "\n```\n\n"
    return markdown


def guardar_texto_en_archivo(texto, nombre_archivo="salida.md"):
    """
    Escribe 'texto' en un archivo en disco usando codificación UTF-8.
    """
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(texto)
        return True
    except Exception as e:
        print(f"Error al guardar el archivo {nombre_archivo}: {e}")
        return False


def guardar_log(texto, nombre_archivo="log_llm.txt"):
    """
    Agrega la cadena 'texto' a un archivo log, para registrar todas las interacciones.
    """
    try:
        with open(nombre_archivo, "a", encoding="utf-8") as f:
            f.write(texto + "\n\n")
        return True
    except Exception as e:
        print(f"Error al guardar log: {e}")
        return False


###############################################################################
#                           Llamadas al LLM
###############################################################################

def call_llm_single_object(prompt_text):
    """
    Ejemplo de llamada genérica a Google Gemini usando la configuración
    de response_schema, que devuelve un único objeto con "path_file" y "content".
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-2.0-pro-exp-02-05"

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt_text),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=64,
        max_output_tokens=8192,
        response_mime_type="application/json",
        # Aquí definimos el esquema de la respuesta: un objeto con 2 campos obligatorios
        response_schema=types.Schema(
            type=types.Type.OBJECT,
            required=["path_file", "content"],
            properties={
                "path_file": types.Schema(type=types.Type.STRING),
                "content": types.Schema(type=types.Type.STRING),
            },
        ),
    )

    respuesta_cruda = ""
    for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
    ):
        respuesta_cruda += chunk.text

    return respuesta_cruda


def llamar_llm_usuario_inicial(descripcion_tarea, archivos_nivel_1):
    """
    Envía al LLM la lista (archivos_nivel_1) y la tarea del usuario (descripcion_tarea),
    retornando un dict con la clave `files_needed` (lista de nombres).
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-2.0-pro-exp-02-05"

    prompt = (
        f"Tu tarea es: {descripcion_tarea}\n"
        f"Archivos/carpetas a primer nivel: {archivos_nivel_1}\n\n"
        f"- Devuelve un JSON con la propiedad 'files_needed' (una lista con los nombres).\n"
        f"- Esta lista que devolverás serán los nombres que te estoy proporcionando.\n"
        f"- Solo debes devolver los nombres de los archivos/carpetas que se te envían.\n"
        "- Se extraerá el contenido de los archivos que selecciones, para que sea usado para otro prompt. "
        f"Por tanto debes devolver solo los nombres de los archivos/carpetas que necesitas para cumplir la tarea."
    )

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=64,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=types.Schema(
            type=types.Type.OBJECT,
            required=["files_needed"],
            properties={
                "files_needed": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING),
                )
            },
        ),
    )

    raw_response = ""
    for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
    ):
        raw_response += chunk.text

    log_text = (
            "PROMPT (llamar_llm_usuario_inicial):\n" + prompt +
            "\n---\nRaw Response:\n" + raw_response
    )
    guardar_log(log_text)

    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError:
        data = {"files_needed": []}

    return data


def llamar_llm_eleccion_final_markdown(descripcion_tarea, markdown):
    """
    Envía al LLM un Markdown con el contenido y la tarea para obtener
    una lista con las rutas necesarias en `files_needed`.
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-2.0-pro-exp-02-05"

    prompt = (
        f"Tu tarea es: {descripcion_tarea}\n\n"
        "El proyecto a evaluar es el siguiente:\n"
        "\n\n---------------------------------\n\n"
        f"{markdown}"
        "\n\n---------------------------------\n\n"
        "- Devuelve un JSON con la clave `files_needed` (lista con rutas relativas necesarias).\n"
        "- Debes tomar en cuenta solo el contenido del proyecto.\n"
        "- Solo debes devolver las rutas relativas de los archivos que se pueden tomar como ejemplo o referencia.\n"
        "- Repito, estrictamente debes retornar solo las rutas relativas que se encuentran en el proyecto, y que sean "
        "necesarias para tomarlas como ejemplo o referencia para abordar tu tarea.\n"
        "- Trata de obtener al menos un ejemplo\n"
        "- Se extraerá el contenido de los archivos que selecciones, para que sea usado para otro prompt. "
        f"Por tanto debes devolver solo los nombres de los archivos que necesitas para cumplir la tarea."
    )

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=64,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=types.Schema(
            type=types.Type.OBJECT,
            required=["files_needed"],
            properties={
                "files_needed": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING),
                )
            },
        ),
    )

    raw_response = ""
    for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
    ):
        raw_response += chunk.text

    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError:
        data = {"files_needed": []}

    log_text = "PROMPT (llamar_llm_eleccion_final_markdown):\n" + prompt + "\n---\nRespuesta:\n" + json.dumps(data)
    guardar_log(log_text)

    return data


def llamar_llm_crear_plan(descripcion_tarea, markdown):
    """
    Envía al LLM la tarea y el markdown relevante, y pide un plan de pasos.
    Aquí se simula, pero en un escenario real se podría usar un LLM que devuelva
    un array de strings (cada string es un paso).
    """
    prompt = (
        f"Descripción de la tarea: {descripcion_tarea}\n\n"
        "Basado en el contenido a analizar, devuélveme una lista de pasos para cumplir dicha tarea.\n"
        "Ejemplo: [\"Paso 1: ...\", \"Paso 2: ...\"]"
    )

    # Simulación
    plan = [
        "Paso 1: Analizar la estructura del proyecto",
        "Paso 2: Implementar los componentes base",
        "Paso 3: Integrar la funcionalidad principal"
    ]

    log_text = "PROMPT (llamar_llm_crear_plan):\n" + prompt + "\n---\nRespuesta (simulada):\n" + json.dumps(plan)
    guardar_log(log_text)

    return plan


def llamar_llm_ejecutar_paso(descripcion_tarea, paso_adj, markdown):
    """
    Envía al LLM la tarea, el paso especificado y el contenido en 'markdown'.
    Utiliza la snippet de 'call_llm_single_object' y convierte la respuesta en
    un array de un solo ítem (o múltiples, si así deseas).
    
    IMPORTANTE: El schema en 'call_llm_single_object' produce un OBJETO individual
    con 'path_file' y 'content'. Para un escenario con varios archivos devueltos,
    se podría:
       - Llamar varias veces (una por archivo).
       - Cambiar la estrategia del JSON schema para que sea una lista.
    """
    prompt = (
        f"Descripción de la tarea: {descripcion_tarea}\n"
        f"Paso actual a realizar: {paso_adj}\n\n"
        "Contexto (Markdown):\n"
        f"{markdown}\n\n"
        "Por favor, devuelve un JSON con 'path_file' y 'content' para este paso."
    )

    # Llamamos a la función que configura el schema (para un solo objeto).
    respuesta_cruda = call_llm_single_object(prompt)

    # Guardamos la respuesta en el log
    log_text = (
        f"PROMPT (llamar_llm_ejecutar_paso):\n{prompt}\n---\n"
        f"RESPUESTA:\n{respuesta_cruda}"
    )
    guardar_log(log_text)

    # Parseamos la respuesta como JSON, que debería tener { "path_file": ..., "content": ... }
    try:
        data = json.loads(respuesta_cruda)
        # Lo convertimos a la estructura que el sistema internamente maneja (lista de dicts)
        return [
            {
                "file_path": data["path_file"],
                "content": data["content"]
            }
        ]
    except Exception as e:
        print("Error parseando la respuesta del LLM:", e)
        # En caso de error, simulamos una respuesta vacía
        return []


###############################################################################
#                     Lógica de la interfaz con Tkinter
###############################################################################

class AppMapeoArchivos(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mapeo de Archivos del Proyecto - Reestructurado")

        # Variables de estado
        self.ruta_proyecto = StringVar()
        self.descripcion_tarea = StringVar()

        # Frame selección de carpeta
        frame_ruta = tk.Frame(self)
        frame_ruta.pack(padx=10, pady=5, fill="x")
        tk.Label(frame_ruta, text="Ruta del Proyecto:").pack(side="left")
        tk.Entry(frame_ruta, textvariable=self.ruta_proyecto, width=50).pack(side="left", padx=5)
        tk.Button(frame_ruta, text="Seleccionar", command=self.seleccionar_carpeta).pack(side="left")

        # Frame descripción de tarea
        frame_tarea = tk.Frame(self)
        frame_tarea.pack(padx=10, pady=5, fill="x")
        tk.Label(frame_tarea, text="Tarea principal:").pack(side="left")
        tk.Entry(frame_tarea, textvariable=self.descripcion_tarea, width=60).pack(side="left", padx=5)

        # Frame extensiones
        self.frame_extensiones = tk.Frame(self)
        self.frame_extensiones.pack(padx=10, pady=5, fill="x")
        tk.Label(self.frame_extensiones, text="Extensiones de archivo a evaluar:").pack()

        self.lista_extensiones = tk.Listbox(self.frame_extensiones, height=6)
        self.lista_extensiones.pack(fill="both", padx=5, pady=5)

        frame_botones_ext = tk.Frame(self)
        frame_botones_ext.pack(padx=10, pady=5, fill="x")
        tk.Button(frame_botones_ext, text="Agregar", command=self.agregar_extension).pack(side="left", padx=5)
        tk.Button(frame_botones_ext, text="Eliminar", command=self.eliminar_extension).pack(side="left", padx=5)

        # Botón principal de iniciar proceso
        tk.Button(self, text="Iniciar Proceso", command=self.iniciar_proceso).pack(pady=10)

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta del proyecto")
        if carpeta:
            self.ruta_proyecto.set(carpeta)

    def agregar_extension(self):
        ext = simpledialog.askstring("Agregar Extensión", "Ingrese la extensión (ej. ts):")
        if ext:
            if not ext.startswith("."):
                ext = "." + ext.lower()
            else:
                ext = ext.lower()
            self.lista_extensiones.insert(tk.END, ext)

    def eliminar_extension(self):
        seleccion = self.lista_extensiones.curselection()
        if seleccion:
            self.lista_extensiones.delete(seleccion[0])

    def iniciar_proceso(self):
        """
        Flujo principal simplificado:
          1. Obtener ruta y tarea.
          2. Verificar extensiones.
          3. Listar archivos/carp. primer nivel; LLM sugiere cuáles tomar.
          4. Mostrar modal de selección. (Carpetas y archivos nivel 1).
          5. Generar markdown SÓLO de lo seleccionado.
          6. Llamar al LLM -> elegir subcarpetas relevantes.
          7. Mostrar modal subcarpetas.
          8. Generar markdown final.
          9. Llamar LLM -> crear plan/pasos.
          10. Modal reorden/pasos.
          11. Para cada paso, llamar LLM -> JSON con "path_file","content" y crear/escribir archivo.
        """
        ruta = self.ruta_proyecto.get()
        tarea = self.descripcion_tarea.get()
        if not ruta:
            messagebox.showerror("Error", "Debe seleccionar una carpeta de proyecto.")
            return
        if not tarea.strip():
            messagebox.showerror("Error", "Debe ingresar la descripción de la tarea.")
            return

        extensiones = [self.lista_extensiones.get(idx) for idx in range(self.lista_extensiones.size())]
        if not extensiones:
            messagebox.showerror("Error", "Debe agregar al menos una extensión.")
            return

        # 1) Listar primer nivel
        archivos, carpetas = listar_archivos_directorio(ruta)
        nivel_1 = archivos + carpetas  # Para el LLM

        # 2) Llamar LLM: sugerencia de archivos/carpetas
        llm_respuesta = llamar_llm_usuario_inicial(tarea, nivel_1)
        files_needed = llm_respuesta.get("files_needed", [])

        # 3) Mostrar modal de selección
        seleccion_usuario = self.mostrar_modal_seleccion(ruta, archivos, carpetas, files_needed)
        if not seleccion_usuario:
            return  # Usuario canceló

        # 4) Generar listado de rutas que se van a incluir en el markdown
        paths_a_incluir = []
        for item in seleccion_usuario:
            full_path = os.path.join(ruta, item)
            if os.path.isdir(full_path):
                subfiles = listar_archivos_subcarpetas(full_path, extensiones)
                paths_a_incluir.extend(subfiles)
            else:  # Caso archivo individual
                if os.path.splitext(item)[1].lower() in extensiones:
                    paths_a_incluir.append(full_path)

        markdown_text = obtener_markdown_de_archivos(paths_a_incluir, ruta)
        if not guardar_texto_en_archivo(markdown_text, "salida_nivel_1.md"):
            messagebox.showerror("Error", "No se pudo guardar el markdown inicial.")
            return

        # 5) LLM -> segunda elección más específica
        llm_respuesta_2 = llamar_llm_eleccion_final_markdown(tarea, markdown_text)
        files_needed_2 = llm_respuesta_2.get("files_needed", [])

        # 6) Modal para subcarpetas/archivos reales
        seleccion_sub = self.mostrar_modal_seleccion_subcarpetas(ruta, paths_a_incluir, files_needed_2)
        if not seleccion_sub:
            return

        markdown_final = obtener_markdown_de_archivos(seleccion_sub, ruta)
        if not guardar_texto_en_archivo(markdown_final, "salida_final.md"):
            messagebox.showerror("Error", "No se pudo guardar el markdown final.")
            return

        # 7) Crear un plan/pasos
        plan_pasos = llamar_llm_crear_plan(tarea, markdown_final)
        pasos_confirmados = self.mostrar_modal_reordenar_pasos(plan_pasos)
        if not pasos_confirmados:
            return

        # 8) Iterar pasos y aplicar cambios
        for idx, paso in enumerate(pasos_confirmados, start=1):
            resultados_paso = llamar_llm_ejecutar_paso(tarea, paso, markdown_final)
            # Aplicar cambios en disco
            for obj in resultados_paso:
                path_file = obj.get("file_path", "")
                content = obj.get("content", "")
                if not path_file:
                    continue

                full_path = os.path.join(ruta, path_file)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                try:
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception as e:
                    print(f"Error al escribir en {full_path}: {e}")

        messagebox.showinfo("Finalizado", "La reestructuración se ha completado.")

    ########################### Modales de selección ############################
    def mostrar_modal_seleccion(self, ruta_base, archivos, carpetas, preseleccion):
        modal = Toplevel(self)
        modal.title("Select first\-level items")
        modal.geometry("600x400")

        frame_tree = tk.Frame(modal)
        frame_tree.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        tree = ttk.Treeview(frame_tree, yscrollcommand=scrollbar.set, selectmode="extended")
        tree.pack(fill="both", expand=True)

        for item in archivos + carpetas:
            node = tree.insert("", "end", text=item)
            if item in preseleccion:
                tree.selection_add(node)

        scrollbar.config(command=tree.yview)

        selected_items = []

        def confirmar():
            for sel in tree.selection():
                if tree.winfo_exists():
                    selected_items.append(tree.item(sel)["text"])

            modal.destroy()

        def cancelar():
            modal.destroy()

        tk.Button(modal, text="Confirm", command=confirmar).pack(side="left", padx=5, pady=5)
        tk.Button(modal, text="Cancel", command=cancelar).pack(side="left", padx=5, pady=5)

        self.wait_window(modal)
        return selected_items

    def mostrar_modal_seleccion_subcarpetas(self, ruta_base, paths_encontrados, preseleccion_llm):
        modal = Toplevel(self)
        modal.title("Select second\-level items")
        modal.geometry("600x400")

        frame_tree = tk.Frame(modal)
        frame_tree.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        tree = ttk.Treeview(frame_tree, yscrollcommand=scrollbar.set, selectmode="extended")
        tree.pack(fill="both", expand=True)

        unique_paths = list(set(paths_encontrados))
        for p in unique_paths:
            relpath = os.path.relpath(p, ruta_base)
            node = tree.insert("", "end", text=relpath)
            if relpath in preseleccion_llm:
                tree.selection_add(node)

        scrollbar.config(command=tree.yview)

        selected_paths = []

        def confirmar():
            for sel in tree.selection():
                item_text = tree.item(sel)["text"]
                for path in unique_paths:
                    if os.path.relpath(path, ruta_base) == item_text:
                        selected_paths.append(path)
            modal.destroy()

        def cancelar():
            modal.destroy()

        tk.Button(modal, text="Confirm", command=confirmar).pack(side="left", padx=5, pady=5)
        tk.Button(modal, text="Cancel", command=cancelar).pack(side="left", padx=5, pady=5)

        self.wait_window(modal)
        return selected_paths

    def mostrar_modal_reordenar_pasos(self, pasos_iniciales):
        """
        Modal simplificado que muestra y deja editar (en un Text) la lista de pasos.
        Retorna la lista resultante. (Sin reordenamiento dinámico completo, pero se podría implementar).
        """
        modal = Toplevel(self)
        modal.title("Revisar/Editar pasos")

        pasos_final = pasos_iniciales[:]

        text_widget = tk.Text(modal, width=80, height=10)
        text_widget.pack()
        text_widget.insert(tk.END, "\n".join(pasos_final))

        def confirmar():
            nuevo = text_widget.get("1.0", tk.END).strip().split("\n")
            pasos_final.clear()
            pasos_final.extend(nuevo)
            modal.destroy()

        def cancelar():
            pasos_final.clear()
            modal.destroy()

        tk.Button(modal, text="Confirmar", command=confirmar).pack(side="left", padx=5, pady=5)
        tk.Button(modal, text="Cancelar", command=cancelar).pack(side="left", padx=5, pady=5)

        self.wait_window(modal)
        return pasos_final


###############################################################################
#                          Lanzar la Aplicación
###############################################################################

if __name__ == "__main__":
    app = AppMapeoArchivos()
    app.mainloop()
