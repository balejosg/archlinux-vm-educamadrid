#!/usr/bin/env python3
"""
educamadrid-files.py
====================
Portal Web de Archivos y Vista Previa para Docentes (EducaMadrid).
Escucha en el puerto 80 de la VM (accesible en http://127.0.0.1:8080 desde Windows).
Permite a los docentes:
  - Subir archivos (PDFs, DOCX, imágenes) desde Windows a ~/trabajo con Drag & Drop.
  - Descargar con 1 clic los materiales generados por OpenCode (.html, .gift, .docx, .pdf, .png).
  - Previsualizar en vivo las unidades HTML, PDFs e imágenes antes de subirlos a Moodle.
"""

import os
import sys
import io
import zipfile
import mimetypes
import urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from email.parser import BytesParser
from email.policy import default as email_default

BASE_DIR = os.path.realpath("/home/docente/trabajo")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 80

ICONS = {
    ".html": "🌐",
    ".css": "🎨",
    ".gift": "📝",
    ".xml": "📋",
    ".docx": "📄",
    ".md": "📑",
    ".pdf": "📕",
    ".png": "🖼️",
    ".jpg": "🖼️",
    ".jpeg": "🖼️",
    ".svg": "🖼️",
    ".dot": "🔗",
    ".py": "⚙️",
}

def safe_join(rel_path: str) -> str:
    cleaned = urllib.parse.unquote(rel_path).lstrip("/")
    full = os.path.realpath(os.path.join(BASE_DIR, cleaned))
    if not full.startswith(BASE_DIR):
        return BASE_DIR
    return full

def fmt_size(num: float) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if num < 1024.0:
            return f"{num:.0f} {unit}" if unit == "B" else f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} TB"

class EducaMadridHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        target = safe_join(parsed.path)

        if not os.path.exists(target):
            self.send_error(404, "Archivo o carpeta no encontrado")
            return

        if os.path.isdir(target):
            if qs.get("zip") == ["1"]:
                self.serve_zip(target)
            else:
                self.serve_directory(target, parsed.path)
        else:
            force_dl = qs.get("download") == ["1"]
            self.serve_file(target, force_dl)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        target_dir = safe_join(parsed.path)
        if not os.path.isdir(target_dir):
            target_dir = BASE_DIR

        content_type = self.headers.get("Content-Type", "")
        content_len = int(self.headers.get("Content-Length", "0"))
        if content_len <= 0 or "multipart/form-data" not in content_type:
            self.send_response(303)
            self.send_header("Location", parsed.path or "/")
            self.end_headers()
            return

        body = self.rfile.read(content_len)
        raw_msg = b"Content-Type: " + content_type.encode("utf-8") + b"\r\n\r\n" + body
        msg = BytesParser(policy=email_default).parsebytes(raw_msg)

        saved = 0
        for part in msg.iter_parts():
            filename = part.get_filename()
            if filename:
                safe_name = os.path.basename(filename)
                dest_path = os.path.join(target_dir, safe_name)
                payload = part.get_payload(decode=True)
                if payload is not None:
                    with open(dest_path, "wb") as f:
                        f.write(payload)
                    try:
                        import pwd
                        pw = pwd.getpwnam("docente")
                        os.chown(dest_path, pw.pw_uid, pw.pw_gid)
                    except Exception:
                        pass
                    saved += 1

        loc = (parsed.path or "/") + f"?uploaded={saved}"
        self.send_response(303)
        self.send_header("Location", loc)
        self.end_headers()

    def serve_file(self, filepath: str, force_download: bool):
        ctype, _ = mimetypes.guess_type(filepath)
        if not ctype:
            if filepath.endswith((".gift", ".md", ".dot", ".py")):
                ctype = "text/plain; charset=utf-8"
            else:
                ctype = "application/octet-stream"
        elif ctype.startswith("text/") or ctype in ("application/xml", "application/json"):
            ctype += "; charset=utf-8"

        try:
            with open(filepath, "rb") as f:
                data = f.read()
        except Exception as e:
            self.send_error(500, str(e))
            return

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if force_download:
            fname = os.path.basename(filepath)
            self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
        self.end_headers()
        self.wfile.write(data)

    def serve_zip(self, dirpath: str):
        buf = io.BytesIO()
        folder_name = os.path.basename(dirpath) or "trabajo-educamadrid"
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(dirpath):
                for file in files:
                    full = os.path.join(root, file)
                    arcname = os.path.relpath(full, dirpath)
                    zf.write(full, arcname)
        data = buf.getvalue()
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", f'attachment; filename="{folder_name}.zip"')
        self.end_headers()
        self.wfile.write(data)

    def serve_directory(self, dirpath: str, req_path: str):
        rel = os.path.relpath(dirpath, BASE_DIR)
        if rel == ".":
            rel = ""
        entries = sorted(os.listdir(dirpath), key=lambda x: (not os.path.isdir(os.path.join(dirpath, x)), x.lower()))

        rows = []
        if rel:
            parent_url = "/" + os.path.dirname(rel).lstrip(".")
            rows.append(f"""
            <tr class="hover:bg-slate-800/60 transition">
              <td class="py-3 px-4 font-medium text-rose-400" colspan="4">
                <a href="{parent_url}" class="flex items-center gap-2">⬅️ Volver a la carpeta superior</a>
              </td>
            </tr>""")

        for name in entries:
            if name.startswith("."):
                continue
            full = os.path.join(dirpath, name)
            is_dir = os.path.isdir(full)
            stat = os.stat(full)
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M")
            url_path = "/" + (os.path.join(rel, name) if rel else name)
            url_encoded = urllib.parse.quote(url_path)

            if is_dir:
                rows.append(f"""
                <tr class="hover:bg-slate-800/60 transition">
                  <td class="py-3 px-4 font-semibold text-white">
                    <a href="{url_encoded}/" class="flex items-center gap-2.5 hover:text-rose-300">
                      <span class="text-lg">📁</span> {name}/
                    </a>
                  </td>
                  <td class="py-3 px-4 text-slate-400 text-xs">Carpeta</td>
                  <td class="py-3 px-4 text-slate-400 text-xs">{mtime}</td>
                  <td class="py-3 px-4 text-right space-x-2">
                    <a href="{url_encoded}/" class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium">Abrir</a>
                    <a href="{url_encoded}/?zip=1" class="px-3 py-1 rounded-lg bg-rose-950/80 hover:bg-rose-900 border border-rose-800 text-rose-200 text-xs font-medium">⬇️ ZIP</a>
                  </td>
                </tr>""")
            else:
                _, ext = os.path.splitext(name.lower())
                icon = ICONS.get(ext, "📄")
                size_str = fmt_size(stat.st_size)
                rows.append(f"""
                <tr class="hover:bg-slate-800/60 transition">
                  <td class="py-3 px-4 text-slate-100">
                    <a href="{url_encoded}" target="_blank" class="flex items-center gap-2.5 hover:text-amber-300">
                      <span class="text-lg">{icon}</span> {name}
                    </a>
                  </td>
                  <td class="py-3 px-4 text-slate-400 text-xs font-mono">{size_str}</td>
                  <td class="py-3 px-4 text-slate-400 text-xs">{mtime}</td>
                  <td class="py-3 px-4 text-right space-x-2">
                    <a href="{url_encoded}" target="_blank" class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-300 text-xs font-medium">👁️ Vista Previa</a>
                    <a href="{url_encoded}?download=1" class="px-3 py-1 rounded-lg bg-emerald-950/90 hover:bg-emerald-900 border border-emerald-700/80 text-emerald-200 text-xs font-semibold">⬇️ Descargar</a>
                  </td>
                </tr>""")

        html = f"""<!DOCTYPE html>
<html lang="es" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Archivos ~/trabajo • EducaMadrid OpenCode v2</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans">
  <header class="border-b border-slate-800 bg-slate-900/90 sticky top-0 z-10 backdrop-blur">
    <div class="max-w-5xl mx-auto px-6 py-4 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-rose-600 to-red-700 flex items-center justify-center font-bold text-white shadow">📂</div>
        <div>
          <h1 class="text-lg font-bold text-white">Gestor de Archivos y Vista Previa Docente</h1>
          <p class="text-xs text-slate-400 font-mono">/home/docente/trabajo/{rel}</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a href="?zip=1" class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 transition">
          📦 Descargar Todo (.ZIP)
        </a>
        <a href="http://127.0.0.1:49374" class="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-xs font-bold text-white shadow transition">
          🤖 Volver a OpenCode GUI
        </a>
      </div>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-6 py-8 space-y-6">
    <!-- Panel para subir archivos desde Windows -->
    <form method="POST" enctype="multipart/form-data" class="p-5 rounded-2xl bg-slate-900/80 border border-dashed border-slate-700 hover:border-rose-500/60 transition flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <span class="text-2xl">📤</span>
        <div>
          <h2 class="text-sm font-bold text-white">Subir archivos desde tu ordenador Windows a esta carpeta</h2>
          <p class="text-xs text-slate-400">Sube PDFs, documentos Word (.docx) o imágenes para que OpenCode trabaje con ellos.</p>
        </div>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <input type="file" name="files" multiple required class="text-xs text-slate-300 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-rose-300 hover:file:bg-slate-700 cursor-pointer" />
        <button type="submit" class="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow transition shrink-0">
          Subir a ~/trabajo
        </button>
      </div>
    </form>

    <!-- Tabla de archivos -->
    <div class="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden shadow-xl">
      <table class="w-full text-left border-collapse text-sm">
        <thead>
          <tr class="bg-slate-800/70 text-slate-300 text-xs uppercase tracking-wider">
            <th class="py-3 px-4">Nombre del Archivo / Carpeta</th>
            <th class="py-3 px-4">Tamaño</th>
            <th class="py-3 px-4">Modificado</th>
            <th class="py-3 px-4 text-right">Acciones (Vista Previa / Descarga)</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/70">
          {''.join(rows)}
        </tbody>
      </table>
    </div>
  </main>
</body>
</html>"""
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    os.makedirs(BASE_DIR, exist_ok=True)
    server = HTTPServer(("0.0.0.0", PORT), EducaMadridHandler)
    print(f"EducaMadrid File & Preview Server escuchando en http://0.0.0.0:{PORT} -> {BASE_DIR}")
    server.serve_forever()
