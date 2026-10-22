#!/usr/bin/env python3
"""
limpiar_html_moodle.py
======================
Validador y optimizador de archivos HTML para Moodle / EducaMadrid.

Garantiza:
1. Eliminación de etiquetas peligrosas (<script>, <iframe>, <object>, <embed>, <form>).
2. Supresión de eventos inline (onclick, onload, etc.).
3. Verificación de accesibilidad básica (alt en todas las <img>).
4. Extracción del cuerpo (<div class="contenido-educamadrid"> o <body>) listo para pegar en Atto/TinyMCE.
"""

import sys
import os
import re
from bs4 import BeautifulSoup

TAGS_PROHIBIDOS = ["script", "iframe", "object", "embed", "form", "input", "button", "link"]
ATRIBUTOS_PELIGROSOS = re.compile(r"^on[a-z]+", re.IGNORECASE)

def procesar_html(ruta_entrada: str, ruta_salida: str = None) -> bool:
    if not os.path.isfile(ruta_entrada):
        print(f"❌ Error: El archivo '{ruta_entrada}' no existe.")
        return False

    with open(ruta_entrada, "r", encoding="utf-8") as f:
        contenido = f.read()

    soup = BeautifulSoup(contenido, "html.parser")

    # 1. Eliminar etiquetas no permitidas por Moodle
    eliminadas = 0
    for tag in soup.find_all(TAGS_PROHIBIDOS):
        tag.decompose()
        eliminadas += 1

    # 2. Limpiar atributos javascript / eventos inline
    eventos_limpiados = 0
    for elem in soup.find_all(True):
        attrs = list(elem.attrs.keys())
        for attr in attrs:
            if ATRIBUTOS_PELIGROSOS.match(attr) or "javascript:" in str(elem.attrs[attr]).lower():
                del elem.attrs[attr]
                eventos_limpiados += 1

    # 3. Comprobar accesibilidad de imágenes (etiqueta alt obligatoria DUA)
    imagenes = soup.find_all("img")
    sin_alt = 0
    for img in imagenes:
        if not img.get("alt"):
            img["alt"] = "Imagen didáctica de contenido"
            sin_alt += 1

    # Extraer contenido principal
    contenedor = soup.find("div", class_="contenido-educamadrid")
    if contenedor:
        resultado = str(contenedor)
    elif soup.body:
        resultado = "".join(str(c) for c in soup.body.children if str(c).strip())
    else:
        resultado = str(soup)

    if ruta_salida is None:
        base, ext = os.path.splitext(ruta_entrada)
        ruta_salida = f"{base}_moodle_listo{ext}"

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(resultado)

    print("============================================================")
    print("✅ VALIDACIÓN Y LIMPIEZA PARA EDUCAMADRID COMPLETADA")
    print("============================================================")
    print(f"📄 Archivo origen:  {ruta_entrada}")
    print(f"💾 Archivo destino: {ruta_salida}")
    print(f"🧹 Tags no permitidos eliminados: {eliminadas}")
    print(f"🛡️ Eventos inline desactivados:   {eventos_limpiados}")
    print(f"♿ 'alt' añadidos por DUA:        {sin_alt}")
    print("👉 Listo para copiar y pegar en Atto/TinyMCE o subir como recurso.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 limpiar_html_moodle.py <archivo.html> [archivo_salida.html]")
        sys.exit(1)
    entrada = sys.argv[1]
    salida = sys.argv[2] if len(sys.argv) > 2 else None
    procesar_html(entrada, salida)
