# Mapeo de Archivos a Markdown

Este proyecto consiste en un script en Python que recorre de forma recursiva un directorio, filtra archivos según sus extensiones y extrae su contenido para guardarlo en un único archivo Markdown. Antes de cada archivo se añade su ruta relativa como encabezado, y luego se inserta el contenido dentro de un bloque de código.

## Características

- Recorrido recursivo de directorios.
- Filtrado de archivos basado en extensiones configurables.
- Extracción completa del contenido de cada archivo.
- Generación de un documento Markdown con la ruta relativa (como encabezado) y el contenido del archivo en bloques de código.
- Interfaz gráfica para gestionar la lista de extensiones, selección de carpeta y ejecución del proceso.

## Requisitos

- Python 3.x
- [PyInstaller](https://www.pyinstaller.org/) (para generar el archivo ejecutable)
- (Opcional) [auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/) si deseas una interfaz gráfica para la conversión a .exe.

## Instalación

1. **Clona o descarga el repositorio del proyecto.**

2. **Crea y activa un entorno virtual (recomendado):**

   En Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate
