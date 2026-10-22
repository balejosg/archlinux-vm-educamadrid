#!/usr/bin/env python3
"""
generar_diagrama.py
===================
Compilador de mapas conceptuales y esquemas visuales para EducaMadrid.
Convierte código Graphviz DOT a imágenes PNG y SVG nítidas.
"""

import sys
import os
import subprocess

FORMATOS_VALIDOS = {"png", "svg", "pdf", "jpg", "jpeg", "webp"}

def compilar_dot(dot_path: str, segundo_arg: str = "png") -> bool:
    if not os.path.isfile(dot_path):
        print(f"❌ Error: El archivo '{dot_path}' no existe.")
        return False

    base, _ = os.path.splitext(dot_path)
    if segundo_arg.lower() in FORMATOS_VALIDOS:
        formato = segundo_arg.lower()
        salida = f"{base}.{formato}"
    else:
        salida = segundo_arg
        _, ext = os.path.splitext(salida)
        formato = ext.lstrip(".").lower() if ext else "png"
        if formato not in FORMATOS_VALIDOS:
            formato = "png"

    cmd = ["dot", f"-T{formato}", dot_path, "-o", salida]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"✅ Diagrama generado con éxito: {salida}")
            return True
        else:
            print(f"⚠️ Error de Graphviz: {res.stderr}")
    except FileNotFoundError:
        print("❌ Error: Graphviz ('dot') no está instalado en el sistema.")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 generar_diagrama.py <archivo.dot> [salida.png | png | svg]")
        sys.exit(1)
    archivo = sys.argv[1]
    arg2 = sys.argv[2] if len(sys.argv) > 2 else "png"
    if not compilar_dot(archivo, arg2):
        sys.exit(1)
