#!/usr/bin/env node
/**
 * opencode-gateway.mjs
 * ====================
 * Gateway inverso para OpenCode v2 en ArchLinux-EducaMadrid.
 * Escucha en 0.0.0.0:49374 y redirige tráfico HTTP + WebSockets al servicio
 * interno de OpenCode (127.0.0.1:49375), garantizando:
 *   1. Autenticación transparente (Basic Auth inyectado automáticamente).
 *   2. Interfaz preconfigurada en Español (locale: "es").
 *   3. Proyecto "/home/docente/trabajo" pre-abierto por defecto.
 *   4. Apertura automática de sesión lista para escribir y acceso rápido
 *      al Gestor de Archivos / Vista Previa Web (puerto 8080).
 */

import http from "node:http";
import net from "node:net";

const LISTEN_HOST = "0.0.0.0";
const LISTEN_PORT = 49374;
const TARGET_HOST = "127.0.0.1";
const TARGET_PORT = 49375;
const AUTH_HEADER = "Basic " + Buffer.from("opencode:educamadrid").toString("base64");

const INJECTED_SCRIPT = `<script id="educamadrid-preload">
;(function () {
  try {
    if (!localStorage.getItem("opencode.global.dat:language")) {
      localStorage.setItem("opencode.global.dat:language", JSON.stringify({ locale: "es" }));
    }
    var srvKey = "opencode.global.dat:server";
    var raw = localStorage.getItem(srvKey);
    var parsed = raw ? JSON.parse(raw) : {};
    var originUrl = window.location.origin;
    var list = [{ type: "http", http: { url: originUrl, password: "educamadrid" } }];
    var projects = (parsed.projects && parsed.projects.local && parsed.projects.local.length > 0)
      ? parsed.projects
      : { local: [{ worktree: "/home/docente/trabajo", expanded: true }] };
    var lastProject = (parsed.lastProject && parsed.lastProject.local)
      ? parsed.lastProject
      : { local: "/home/docente/trabajo" };
    localStorage.setItem(srvKey, JSON.stringify({
      list: list,
      hidden: parsed.hidden || {},
      projects: projects,
      lastProject: lastProject,
      recentlyClosed: parsed.recentlyClosed || {}
    }));
  } catch (e) {
    console.warn("EducaMadrid preload error:", e);
  }

  window.addEventListener("DOMContentLoaded", function () {
    // 1. Auto-abrir sesión nueva en la primera visita para que el docente vea directamente el prompt
    if (!sessionStorage.getItem("em_session_init")) {
      var tries = 0;
      var iv = setInterval(function () {
        tries++;
        var btn = document.querySelector('[data-action="home-new-session"]');
        if (btn && window.location.pathname === "/") {
          sessionStorage.setItem("em_session_init", "1");
          clearInterval(iv);
          btn.click();
        }
        if (tries > 35) clearInterval(iv);
      }, 150);
    }

    // 2. Botón flotante para abrir el Gestor de Archivos y Vista Previa (Puerto 8080)
    if (!document.getElementById("em-files-btn")) {
      var btnFiles = document.createElement("a");
      btnFiles.id = "em-files-btn";
      btnFiles.href = "http://" + (window.location.hostname || "127.0.0.1") + ":8080";
      btnFiles.target = "_blank";
      btnFiles.rel = "noopener";
      btnFiles.title = "Subir PDFs/DOCX desde Windows, descargar materiales generados y previsualizar HTML";
      btnFiles.innerHTML = "📂 Archivos ~/trabajo";
      btnFiles.style.cssText = [
        "position:fixed",
        "bottom:14px",
        "right:16px",
        "z-index:99999",
        "background:linear-gradient(135deg,#c70828,#9e001b)",
        "color:#ffffff",
        "font-family:system-ui,-apple-system,sans-serif",
        "font-size:12px",
        "font-weight:600",
        "padding:7px 13px",
        "border-radius:999px",
        "text-decoration:none",
        "box-shadow:0 4px 14px rgba(199,8,40,0.35)",
        "border:1px solid rgba(255,255,255,0.22)",
        "display:inline-flex",
        "align-items:center",
        "gap:6px",
        "transition:transform 0.15s ease,box-shadow 0.15s ease"
      ].join(";");
      btnFiles.onmouseenter = function () {
        btnFiles.style.transform = "translateY(-1px)";
        btnFiles.style.boxShadow = "0 6px 18px rgba(199,8,40,0.5)";
      };
      btnFiles.onmouseleave = function () {
        btnFiles.style.transform = "none";
        btnFiles.style.boxShadow = "0 4px 14px rgba(199,8,40,0.35)";
      };
      document.body.appendChild(btnFiles);
    }
  });
})();
</script>`;

const server = http.createServer((req, res) => {
  const headers = { ...req.headers };
  headers["authorization"] = AUTH_HEADER;
  // Evitar compresión brotli/gzip en HTML para poder inyectar el script limpiamente
  if (req.headers.accept && req.headers.accept.includes("text/html")) {
    delete headers["accept-encoding"];
  }

  const options = {
    hostname: TARGET_HOST,
    port: TARGET_PORT,
    path: req.url,
    method: req.method,
    headers
  };

  const proxyReq = http.request(options, (proxyRes) => {
    const contentType = proxyRes.headers["content-type"] || "";
    if (contentType.includes("text/html")) {
      const chunks = [];
      proxyRes.on("data", (chunk) => chunks.push(chunk));
      proxyRes.on("end", () => {
        let html = Buffer.concat(chunks).toString("utf8");
        html = html.replace("<head>", "<head>\n" + INJECTED_SCRIPT);
        const outHeaders = { ...proxyRes.headers };
        delete outHeaders["content-security-policy"];
        delete outHeaders["content-length"];
        delete outHeaders["content-encoding"];
        res.writeHead(proxyRes.statusCode || 200, outHeaders);
        res.end(html, "utf8");
      });
    } else {
      res.writeHead(proxyRes.statusCode || 200, proxyRes.headers);
      proxyRes.pipe(res);
    }
  });

  proxyReq.on("error", (err) => {
    res.writeHead(502, { "content-type": "application/json; charset=utf-8" });
    res.end(JSON.stringify({ error: "OpenCode backend iniciándose...", detail: err.message }));
  });

  req.pipe(proxyReq);
});

// Soporte completo para WebSockets / Upgrade (SSE, PTY, eventos en tiempo real)
server.on("upgrade", (req, clientSocket, head) => {
  const targetSocket = net.connect(TARGET_PORT, TARGET_HOST, () => {
    const lines = [`${req.method} ${req.url} HTTP/${req.httpVersion}`];
    const headers = { ...req.headers, authorization: AUTH_HEADER };
    for (const [k, v] of Object.entries(headers)) {
      if (Array.isArray(v)) {
        for (const item of v) lines.push(`${k}: ${item}`);
      } else if (v !== undefined) {
        lines.push(`${k}: ${v}`);
      }
    }
    lines.push("", "");
    targetSocket.write(lines.join("\r\n"));
    if (head && head.length) targetSocket.write(head);
    clientSocket.pipe(targetSocket).pipe(clientSocket);
  });

  targetSocket.on("error", () => clientSocket.destroy());
  clientSocket.on("error", () => targetSocket.destroy());
});

server.listen(LISTEN_PORT, LISTEN_HOST, () => {
  console.log(`EducaMadrid OpenCode Gateway escuchando en http://${LISTEN_HOST}:${LISTEN_PORT} -> ${TARGET_HOST}:${TARGET_PORT}`);
});
