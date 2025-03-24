import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Crear archivos desde JSON")
        self.directorio_base = ""
        self.json_file = ""

        # Botón para seleccionar la ruta base
        self.btn_ruta = tk.Button(root, text="Seleccionar ruta", command=self.seleccionar_ruta)
        self.btn_ruta.pack(pady=10)

        # Etiqueta para mostrar la ruta seleccionada
        self.lbl_ruta = tk.Label(root, text="Ruta no seleccionada")
        self.lbl_ruta.pack()

        # Botón para seleccionar el archivo JSON
        self.btn_json = tk.Button(root, text="Seleccionar JSON", command=self.seleccionar_json)
        self.btn_json.pack(pady=10)

        # Etiqueta para mostrar el archivo JSON seleccionado
        self.lbl_json = tk.Label(root, text="JSON no seleccionado")
        self.lbl_json.pack()

        # Botón para confirmar y procesar el JSON
        self.btn_confirmar = tk.Button(root, text="Confirmar", command=self.procesar_json)
        self.btn_confirmar.pack(pady=20)

    def seleccionar_ruta(self):
        ruta = filedialog.askdirectory(title="Seleccionar directorio base")
        if ruta:
            self.directorio_base = ruta
            self.lbl_ruta.config(text=f"Ruta seleccionada: {ruta}")

    def seleccionar_json(self):
        archivo = filedialog.askopenfilename(title="Seleccionar archivo JSON", filetypes=[("JSON files", "*.json")])
        if archivo:
            self.json_file = archivo
            self.lbl_json.config(text=f"Archivo JSON: {archivo}")

    def procesar_json(self):
        if not self.directorio_base:
            messagebox.showerror("Error", "Debe seleccionar una ruta base.")
            return
        if not self.json_file:
            messagebox.showerror("Error", "Debe seleccionar un archivo JSON.")
            return

        try:
            with open(self.json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el JSON: {e}")
            return

        # Procesar cada objeto en el JSON
        for item in data:
            # Aseguramos que el item tenga las claves 'path' y 'content'
            if "path" not in item or "content" not in item:
                messagebox.showwarning("Advertencia",
                                       "Un objeto en el JSON no tiene las claves 'path' o 'content'. Se omitirá.")
                continue

            # Construir la ruta completa combinando la ruta base y el path del archivo
            ruta_completa = os.path.join(self.directorio_base, item["path"])

            # Crear directorios intermedios si no existen
            directorio_archivo = os.path.dirname(ruta_completa)
            os.makedirs(directorio_archivo, exist_ok=True)

            try:
                with open(ruta_completa, "w", encoding="utf-8") as archivo:
                    archivo.write(item["content"])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo escribir el archivo {ruta_completa}: {e}")
                return

        messagebox.showinfo("Éxito", "Todos los archivos se han creado correctamente.")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
