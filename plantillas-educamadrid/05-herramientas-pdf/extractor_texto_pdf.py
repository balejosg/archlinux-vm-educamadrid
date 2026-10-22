#!/usr/bin/env python3
"""
extractor_texto_pdf.py
======================
Herramienta de extracción de texto y tablas de documentos PDF.
Permite a OpenCode y al docente procesar currículos oficiales (BOE/BOCM),
libros de texto y exámenes en PDF para reutilizarlos en el Aula Virtual.
"""

import sys
import os

def extraer_con_pypdf(ruta_pdf: str, ruta_salida_txt: str = None) -> bool:
    try:
        from pypdf import PdfReader
        lector = PdfReader(ruta_pdf)
        num_paginas = len(lector.pages)
        texto_completo = []

        print(f"📄 Leyendo '{ruta_pdf}' ({num_paginas} páginas)...")
        for i, pag in enumerate(lector.pages, 1):
            txt = pag.extract_text() or ""
            texto_completo.append(f"--- PÁGINA {i} ---\n{txt}\n")

        resultado = "\n".join(texto_completo)

        if ruta_salida_txt is None:
            base, _ = os.path.splitext(ruta_pdf)
            ruta_salida_txt = f"{base}_extraido.txt"

        with open(ruta_salida_txt, "w", encoding="utf-8") as f:
            f.write(resultado)

        print(f"✅ Texto extraído correctamente en: {ruta_salida_txt}")
        return True
    except ImportError:
        pass
    except Exception as e:
        print(f"⚠️ Error con pypdf: {e}")
    return False

def extraer_con_pdftotext(ruta_pdf: str, ruta_salida_txt: str = None) -> bool:
    import subprocess
    if ruta_salida_txt is None:
        base, _ = os.path.splitext(ruta_pdf)
        ruta_salida_txt = f"{base}_extraido.txt"
    try:
        res = subprocess.run(["pdftotext", "-layout", ruta_pdf, ruta_salida_txt], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"✅ Texto extraído mediante pdftotext: {ruta_salida_txt}")
            return True
    except FileNotFoundError:
        pass
    return False

def procesar(ruta_pdf: str, ruta_salida_txt: str = None):
    if not os.path.isfile(ruta_pdf):
        print(f"❌ Error: El archivo PDF '{ruta_pdf}' no existe.")
        return

    if not extraer_con_pypdf(ruta_pdf, ruta_salida_txt):
        if not extraer_con_pdftotext(ruta_pdf, ruta_salida_txt):
            print("❌ No se encontró ninguna utilidad de extracción (instalar pypdf o poppler).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 extractor_texto_pdf.py <archivo.pdf> [salida.txt]")
        sys.exit(1)
    procesar(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
