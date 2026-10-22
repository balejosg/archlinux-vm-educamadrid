# Arch Linux VM para Docentes de EducaMadrid (OpenCode v2)

Máquina virtual oficial en formato **VirtualBox Appliance (.ova)** diseñada específicamente para el **profesorado de la Comunidad de Madrid**. 

Su propósito fundamental es proporcionar un entorno ágil, potente y automatizado para **generar, transformar y optimizar contenidos didácticos para las Aulas Virtuales de EducaMadrid (Moodle 4.x)** mediante el agente de inteligencia artificial **OpenCode v2**.

---

## 🚀 Descarga Directa y Enlaces

* 🌐 **Sitio Web Oficial / Portal de Descargas**: [https://balejosg.github.io/archlinux-vm-educamadrid/](https://balejosg.github.io/archlinux-vm-educamadrid/)
* 📖 **Caso de Estudio Técnico**: [https://balejosg.github.io/archlinux-vm-educamadrid/como-se-hizo.html](https://balejosg.github.io/archlinux-vm-educamadrid/como-se-hizo.html)
* 📦 **Descarga directa (.zip, 1.73 GB)**: [ArchLinux-EducaMadrid.ova.zip (v1.0.0)](https://github.com/balejosg/archlinux-vm-educamadrid/releases/download/v1.0.0/ArchLinux-EducaMadrid.ova.zip)
* 🔒 **SHA-256 (ZIP)**: `165f65c738bedbd55cc2c1086afd5e104d8195bfb1cdadaf7ee7961868652b7a`
* 🔒 **SHA-256 (OVA descomprimido)**: `63f419f29805bb4b0a51ba87d407c59eaac145bdb41735e8d68365cacc328d6d`

---

## 🎯 Enfoque Pedagógico Docente (Anti-Socrático)

A diferencia de las máquinas virtuales dirigidas a estudiantes de programación:
1. **🚫 Cero Rodeos Socráticos**: El agente interactúa con un **docente**, no con un alumno aprendiendo a programar. Responde de forma directa, resolutiva y con materiales completos listos para publicar.
2. **🚫 Sin Cargas de Java ni Sysadmin**: Se ha eliminado todo el ecosistema de Java (OpenJDK, Maven) y de administración de sistemas/sostenibilidad (Docker, MQTT, monitores de energía).
3. **🤖 OpenCode v2 como Único Agente**: Preinstalado como el motor de IA estándar, utilizable tanto desde la terminal (`opencode`) como a través de su interfaz web sincronizada (`opencode serve --port 49374`).

---

## 🛠️ Capacidades Multiformato Integradas

| Formato | Herramientas en el Sistema | ¿Qué permite hacer al Docente? |
| :--- | :--- | :--- |
| **🌐 HTML Moodle** | `estilos-educamadrid.css`, `limpiar_html_moodle.py`, BeautifulSoup4 | Diseñar lecciones atractivas con tarjetas didácticas, desplegables interactivos sin JS, tablas responsivas y validador de seguridad para Atto/TinyMCE. |
| **📝 Cuestionarios** | `generador_gift.py`, Moodle XML | Generar bancos completos de preguntas tipo test, V/F, emparejamiento y respuesta corta con retroalimentación para importar al Banco de Preguntas. |
| **📄 Documentos** | Pandoc (binario autónomo), `python-docx` | Crear guías docentes, situaciones de aprendizaje y rúbricas LOMLOE tabuladas en formato DOCX y Markdown sin dependencias pesadas de escritorio. |
| **📚 PDFs** | `pdfplumber`, `pypdf`, `weasyprint`, Poppler | Analizar libros de texto y currículos oficiales en PDF (BOE/BOCM) y compilar resúmenes de apuntes de alta fidelidad. |
| **🖼️ Imágenes** | ImageMagick, OptiPNG, Jpegoptim, Graphviz (`dot`) | Comprimir imágenes para no exceder cuotas de disco en el aula virtual (&lt;350 KB) y generar mapas conceptuales automáticos. |

---

## 🔑 Credenciales y Configuración de Red

| Parámetro | Valor |
| :--- | :--- |
| **Usuario Principal** | `docente` (o alternativo `alumno`) |
| **Contraseña** | `docente` (o `alumno`) |
| **Permisos de Administrador** | Acceso `sudo` sin contraseña |
| **Reenvío SSH** | Puerto anfitrión `2222` ➔ Puerto VM `22` (`ssh -p 2222 docente@localhost`) |
| **Servidor Web OpenCode v2** | Puerto anfitrión `49374` ➔ Puerto VM `49374` (`http://localhost:49374`) |
| **Previsualización Web** | Puerto anfitrión `8080` ➔ Puerto VM `80` |
| **Carpeta Compartida Host** | Preconfigurada en `/home/docente/trabajo` |

---

## 📂 Organización del Espacio de Trabajo (`~/trabajo`)

```text
~/trabajo/
├── 01-unidades-html/          # Plantillas HTML, estilos EducaMadrid y limpiador de código Moodle
├── 02-cuestionarios-moodle/   # Bancos de preguntas en formato GIFT y Moodle XML
├── 03-fichas-y-tareas-docs/   # Guías docentes, situaciones de aprendizaje y rúbricas en DOCX
├── 04-material-multimedia/    # Herramientas de optimización de imágenes y esquemas Graphviz
├── 05-herramientas-pdf/       # Extractor de texto de currículos oficiales y compilador a PDF
├── AGENTS.md                  # Directrices del asistente pedagógico directo
└── LEEME.md                   # Guía de inicio rápido con ejemplos prácticos
```

---

## 💡 Cómo Empezar a Usar OpenCode v2

1. Abre la terminal dentro de la máquina virtual (o mediante SSH desde tu ordenador):
   ```bash
   cd ~/trabajo
   opencode
   ```
2. O inicia el servidor web de OpenCode v2 para trabajar directamente desde el navegador de tu ordenador anfitrión:
   ```bash
   opencode serve --port 49374
   ```
   Abre en tu navegador: **`http://localhost:49374`**

### Ejemplos de Peticiones:
* *«Crea una lección en HTML sobre la fotosíntesis para 1º ESO usando las cajas de aviso y desplegables de estilos-educamadrid.css»*
* *«A partir de este texto, genera 8 preguntas tipo test en formato GIFT con justificación en las respuestas correctas e incorrectas»*
* *«Diseña una rúbrica en formato DOCX para evaluar una presentación oral en 4 niveles de logro según el criterio 1.2 de la LOMLOE»*
* *«Optimiza todas las imágenes de la carpeta para que pesen menos de 300 KB y se vean nítidas en Moodle»*
