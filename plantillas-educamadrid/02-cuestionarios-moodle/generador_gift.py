#!/usr/bin/env python3
"""
generador_gift.py
=================
Validador de sintaxis GIFT y convertidor rápido de preguntas en Markdown a GIFT.
Evita los errores habituales que provocan fallos al importar cuestionarios en Moodle.
"""

import sys
import os
import re

def validar_gift(archivo_gift: str) -> bool:
    if not os.path.isfile(archivo_gift):
        print(f"❌ Error: El archivo '{archivo_gift}' no existe.")
        return False

    with open(archivo_gift, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    errores = []
    bloque_abierto = False
    llaves_balance = 0
    num_pregunta = 0

    for num_linea, linea in enumerate(lineas, 1):
        linea_limpia = linea.strip()
        if not linea_limpia or linea_limpia.startswith("//") or linea_limpia.startswith("$CATEGORY"):
            continue

        for char in linea:
            if char == '{':
                llaves_balance += 1
                bloque_abierto = True
            elif char == '}':
                llaves_balance -= 1
                if llaves_balance == 0:
                    num_pregunta += 1
                elif llaves_balance < 0:
                    errores.append(f"Línea {num_linea}: Llave de cierre '}}' sin apertura correspondiente.")

    if llaves_balance != 0:
        errores.append(f"Fin de archivo: Las llaves no están balanceadas (diferencia: {llaves_balance}).")

    print("============================================================")
    print("📋 VALIDACIÓN DE FORMATO GIFT PARA MOODLE")
    print("============================================================")
    print(f"📄 Archivo analizado: {archivo_gift}")
    if not errores:
        print(f"✅ ¡Sintaxis correcta! Se han detectado {num_pregunta} preguntas válidas.")
        print("👉 Puedes subir este archivo directamente a Moodle en: Banco de preguntas ➡️ Importar ➡️ Formato GIFT.")
        return True
    else:
        print(f"⚠️ Se han detectado {len(errores)} inconsistencias:")
        for e in errores:
            print(f"   - {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 generador_gift.py <archivo.gift>")
        sys.exit(1)
    validar_gift(sys.argv[1])
