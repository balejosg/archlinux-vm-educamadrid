#!/usr/bin/env python3
"""
optimizar_imagen.py
===================
Optimizador de imágenes para Aulas Virtuales de EducaMadrid (Moodle).
Reduce el peso de imágenes PNG, JPG y WebP para que carguen rápido y no agoten
la cuota de almacenamiento del centro educativo (< 350 KB).
"""

import sys
import os
import subprocess

def optimizar_con_pillow(ruta_origen: str, ruta_destino: str, max_ancho: int = 1200, calidad: int = 80) -> bool:
    try:
        from PIL import Image
        img = Image.open(ruta_origen)
        
        # Redimensionar si supera el ancho máximo
        if img.width > max_ancho:
            proporcion = max_ancho / float(img.width)
            nuevo_alto = int(float(img.height) * proporcion)
            img = img.resize((max_ancho, nuevo_alto), Image.Resampling.LANCZOS)

        # Convertir RGBA a RGB si se guarda en JPEG
        if ruta_destino.lower().endswith((".jpg", ".jpeg")) and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.save(ruta_destino, optimize=True, quality=calidad)
        peso_kb = os.path.getsize(ruta_destino) / 1024
        print(f"✅ Imagen optimizada con éxito: {ruta_destino} ({peso_kb:.1f} KB)")
        return True
    except ImportError:
        pass
    except Exception as e:
        print(f"⚠️ Error con Pillow: {e}")
    return False

def optimizar_con_imagemagick(ruta_origen: str, ruta_destino: str, max_ancho: int = 1200) -> bool:
    cmd_tool = "magick" if subprocess.run(["which", "magick"], capture_output=True).returncode == 0 else "convert"
    cmd = [cmd_tool, ruta_origen, "-resize", f"{max_ancho}x>", "-quality", "82", ruta_destino]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            peso_kb = os.path.getsize(ruta_destino) / 1024
            print(f"✅ Imagen optimizada con ImageMagick: {ruta_destino} ({peso_kb:.1f} KB)")
            return True
    except FileNotFoundError:
        pass
    return False

def procesar(origen: str, destino: str = None):
    if not os.path.isfile(origen):
        print(f"❌ Error: El archivo '{origen}' no existe.")
        return

    if destino is None:
        base, ext = os.path.splitext(origen)
        destino = f"{base}_opt{ext}"

    if not optimizar_con_pillow(origen, destino):
        if not optimizar_con_imagemagick(origen, destino):
            print("❌ No se pudo optimizar la imagen (se requiere Pillow o ImageMagick).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 optimizar_imagen.py <imagen_original> [imagen_destino]")
        sys.exit(1)
    origen = sys.argv[1]
    destino = sys.argv[2] if len(sys.argv) > 2 else None
    procesar(origen, destino)
