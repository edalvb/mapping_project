import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def seleccionar_carpeta():
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta del proyecto")
    if carpeta:
        ruta_entry.delete(0, tk.END)
        ruta_entry.insert(0, carpeta)

def agregar_extension():
    ext = simpledialog.askstring("Agregar Extensión", "Ingrese la extensión (ej. ts):")
    if ext:
        # Asegurarse de que tenga el punto y esté en minúsculas
        if not ext.startswith("."):
            ext = "." + ext.lower()
        else:
            ext = ext.lower()
        lista_extensiones.insert(tk.END, ext)

def eliminar_extension():
    seleccion = lista_extensiones.curselection()
    if seleccion:
        lista_extensiones.delete(seleccion[0])

def iniciar_mapeo():
    ruta = ruta_entry.get()
    if not ruta:
        messagebox.showerror("Error", "Debe seleccionar una carpeta de proyecto.")
        return
    # Obtener la lista de extensiones de la lista
    extensiones = [lista_extensiones.get(idx) for idx in range(lista_extensiones.size())]
    if not extensiones:
        messagebox.showerror("Error", "Debe agregar al menos una extensión.")
        return

    output = "salida.md"
    try:
        with open(output, "w", encoding="utf-8") as out:
            out.write("# Mapeo de Archivos del Proyecto\n\n")
            for root, dirs, files in os.walk(ruta):
                for file in files:
                    ruta_completa = os.path.join(root, file)
                    ext_actual = os.path.splitext(file)[1].lower()
                    if ext_actual in extensiones:
                        ruta_relativa = os.path.relpath(ruta_completa, ruta)
                        out.write(f"## {ruta_relativa}\n\n")
                        out.write("```plaintext\n")
                        try:
                            with open(ruta_completa, "r", encoding="utf-8") as f:
                                contenido = f.read()
                        except Exception as e:
                            contenido = f"Error al leer el archivo: {e}"
                        out.write(contenido)
                        out.write("\n```\n\n")
        messagebox.showinfo("Éxito", f"Archivo Markdown generado: {output}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear el archivo de salida: {e}")

# Configuración de la interfaz Tkinter
root = tk.Tk()
root.title("Mapeo de Archivos del Proyecto")

# Selección de la carpeta
frame_ruta = tk.Frame(root)
frame_ruta.pack(padx=10, pady=5, fill="x")

ruta_label = tk.Label(frame_ruta, text="Ruta del Proyecto:")
ruta_label.pack(side="left")

ruta_entry = tk.Entry(frame_ruta, width=50)
ruta_entry.pack(side="left", padx=5)

btn_seleccionar = tk.Button(frame_ruta, text="Seleccionar", command=seleccionar_carpeta)
btn_seleccionar.pack(side="left")

# Lista de extensiones
frame_ext = tk.Frame(root)
frame_ext.pack(padx=10, pady=5, fill="x")

ext_label = tk.Label(frame_ext, text="Extensiones:")
ext_label.pack()

lista_extensiones = tk.Listbox(frame_ext, height=6)
lista_extensiones.pack(fill="both", padx=5, pady=5)

frame_botones_ext = tk.Frame(root)
frame_botones_ext.pack(padx=10, pady=5, fill="x")

btn_agregar = tk.Button(frame_botones_ext, text="Agregar", command=agregar_extension)
btn_agregar.pack(side="left", padx=5)

btn_eliminar = tk.Button(frame_botones_ext, text="Eliminar", command=eliminar_extension)
btn_eliminar.pack(side="left", padx=5)

# Botón para iniciar el mapeo
btn_iniciar = tk.Button(root, text="Iniciar Mapeo", command=iniciar_mapeo)
btn_iniciar.pack(pady=10)

root.mainloop()
