#!/usr/bin/env python3
"""
exportar_a_docx.py
==================
Generador de documentos DOCX a partir de archivos Markdown o datos estructurados.
Utiliza Pandoc o python-docx para producir documentos maquetados profesionalmente.
"""

import sys
import os
import subprocess

def convertir_md_a_docx(md_path: str, docx_path: str = None) -> bool:
    if not os.path.isfile(md_path):
        print(f"❌ Error: El archivo '{md_path}' no existe.")
        return False

    if docx_path is None:
        base, _ = os.path.splitext(md_path)
        docx_path = f"{base}.docx"

    print(f"📄 Procesando '{md_path}'...")

    # Intentar primero con Pandoc (maneja tablas, listas y formato complejo)
    try:
        cmd = ["pandoc", md_path, "-o", docx_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"✅ Documento generado con éxito mediante Pandoc: {docx_path}")
            return True
    except FileNotFoundError:
        pass

    # Si Pandoc no estuviera disponible, usar python-docx como respaldo
    try:
        from docx import Document
        doc = Document()
        with open(md_path, "r", encoding="utf-8") as f:
            for linea in f:
                l = linea.rstrip()
                if l.startswith("# "):
                    doc.add_heading(l[2:], level=1)
                elif l.startswith("## "):
                    doc.add_heading(l[3:], level=2)
                elif l.startswith("### "):
                    doc.add_heading(l[4:], level=3)
                elif l.startswith("* ") or l.startswith("- "):
                    doc.add_paragraph(l[2:], style='List Bullet')
                elif l:
                    doc.add_paragraph(l)
        doc.save(docx_path)
        print(f"✅ Documento generado con éxito mediante python-docx: {docx_path}")
        return True
    except ImportError:
        print("❌ Error: No se encontró ni Pandoc ni la librería python-docx.")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 exportar_a_docx.py <archivo.md> [archivo_salida.docx]")
        sys.exit(1)
    entrada = sys.argv[1]
    salida = sys.argv[2] if len(sys.argv) > 2 else None
    convertir_md_a_docx(entrada, salida)
