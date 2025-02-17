import os
import argparse


def main():
    # Configuración de argumentos
    parser = argparse.ArgumentParser(
        description="Script que mapea archivos de un proyecto y extrae su contenido a un Markdown."
    )
    parser.add_argument(
        "ruta",
        help="Ruta raíz del proyecto que se desea mapear."
    )
    parser.add_argument(
        "--extensiones",
        nargs="+",
        required=True,
        help="Lista de extensiones a mapear (por ejemplo: ts tsx css json html)."
    )
    parser.add_argument(
        "--output",
        default="salida.md",
        help="Nombre del archivo Markdown de salida (por defecto: salida.md)."
    )
    args = parser.parse_args()

    # Preparar la lista de extensiones (se normalizan para que incluyan el punto y sean en minúsculas)
    extensiones = []
    for ext in args.extensiones:
        if not ext.startswith("."):
            extensiones.append("." + ext.lower())
        else:
            extensiones.append(ext.lower())

    # Abrir el archivo Markdown de salida
    try:
        with open(args.output, "w", encoding="utf-8") as out:
            out.write("# Mapeo de Archivos del Proyecto\n\n")

            # Recorrer la carpeta de manera recursiva
            for root, dirs, files in os.walk(args.ruta):
                for file in files:
                    # Verificar si la extensión del archivo está en la lista de extensiones a mapear
                    ruta_completa = os.path.join(root, file)
                    ext_actual = os.path.splitext(file)[1].lower()
                    if ext_actual in extensiones:
                        # Calcular la ruta relativa respecto a la ruta raíz
                        ruta_relativa = os.path.relpath(ruta_completa, args.ruta)
                        # Escribir la ruta relativa como título (nivel 2) en el Markdown
                        out.write(f"## {ruta_relativa}\n\n")
                        out.write("```plaintext\n")
                        try:
                            with open(ruta_completa, "r", encoding="utf-8") as f:
                                contenido = f.read()
                        except Exception as e:
                            contenido = f"Error al leer el archivo: {e}"
                        out.write(contenido)
                        out.write("\n```\n\n")
        print(f"Archivo Markdown generado: {args.output}")
    except Exception as e:
        print(f"Error al crear el archivo de salida: {e}")


if __name__ == "__main__":
    main()
