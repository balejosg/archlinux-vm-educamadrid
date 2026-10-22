#!/usr/bin/env python3
"""
generar_pdf_apuntes.py
======================
Generador de guías y apuntes didácticos en PDF de alta fidelidad.
Convierte Markdown o HTML a PDF formateado con estilos tipográficos limpios.
"""

import sys
import os
import subprocess

def compilar_markdown_a_pdf(md_path: str, pdf_path: str = None) -> bool:
    if not os.path.isfile(md_path):
        print(f"❌ Error: El archivo '{md_path}' no existe.")
        return False

    if pdf_path is None:
        base, _ = os.path.splitext(md_path)
        pdf_path = f"{base}.pdf"

    # Intentar primero con Pandoc + Weasyprint / wkhtmltopdf
    try:
        cmd = ["pandoc", md_path, "-o", pdf_path, "--pdf-engine=weasyprint"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"✅ PDF generado con Weasyprint: {pdf_path}")
            return True
    except FileNotFoundError:
        pass

    # Intentar con Pandoc básico
    try:
        cmd = ["pandoc", md_path, "-o", pdf_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"✅ PDF generado con Pandoc: {pdf_path}")
            return True
    except FileNotFoundError:
        pass

    # Intentar con LibreOffice si es un documento intermedio
    try:
        cmd = ["soffice", "--headless", "--convert-to", "pdf", md_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"✅ PDF generado con LibreOffice: {pdf_path}")
            return True
    except FileNotFoundError:
        pass

    print("⚠️ Para compilar a PDF se recomienda tener instalados pandoc y weasyprint o libreoffice.")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 generar_pdf_apuntes.py <archivo.md> [archivo_salida.pdf]")
        sys.exit(1)
    entrada = sys.argv[1]
    salida = sys.argv[2] if len(sys.argv) > 2 else None
    compilar_markdown_a_pdf(entrada, salida)
