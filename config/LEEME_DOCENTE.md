# 🏫 Bienvenido al Entorno de Creación de Contenidos EducaMadrid

Esta máquina virtual está diseñada para facilitar a los **docentes de la Comunidad de Madrid** la creación, adaptación y formateo de materiales educativos para sus **Aulas Virtuales (Moodle 4.x)** mediante **OpenCode v2**.

---

## ⚡ Conexión 1 Clic desde Windows (Sin usar la consola)

El sistema arranca automáticamente todos los servicios en segundo plano al encender la máquina virtual en VirtualBox:

1. **Interfaz Gráfica de OpenCode v2 (`http://localhost:49374`)**:
   * Ejecuta `OpenCode-EducaMadrid.exe` (o `Iniciar-OpenCode.bat`) en tu Windows.
   * Se abre en modo ventana de aplicación dedicada, en español y directamente situada en tu carpeta `~/trabajo`.
2. **Gestor de Archivos y Vista Previa Web (`http://localhost:8080`)**:
   * Haz clic en el botón rojo **`📂 Archivos ~/trabajo`** (esquina inferior derecha de OpenCode) o abre `http://localhost:8080`.
   * Permite **subir PDFs, documentos Word o imágenes** desde tu Windows a `~/trabajo`, **previsualizar lecciones HTML** en vivo y **descargar con 1 clic** (`.docx`, `.pdf`, `.gift`, `.html`, `.zip`) los recursos creados por el agente.
3. **Uso desde terminal (opcional)**:
   * Si prefieres la consola: `cd ~/trabajo && opencode` (se conecta al mismo servicio activo sin conflictos).

---

## 🪄 Comandos Rápidos (`/`) Preconfigurados en OpenCode

Escribe `/` en el cuadro de diálogo de OpenCode para usar las plantillas pedagógicas integradas:

* **`/unidad-html <tema y curso>`**: Crea una lección HTML completa con estilos de EducaMadrid y la valida para Moodle.
* **`/cuestionario-gift <tema y nº preguntas>`**: Genera un banco de preguntas GIFT con retroalimentación y verifica su sintaxis.
* **`/rubrica-lomloe <actividad o criterio>`**: Diseña una rúbrica LOMLOE tabulada y la exporta automáticamente a Word (`.docx`).
* **`/apuntes-pdf <tema>`**: Redacta apuntes o fichas de estudio y los compila a PDF de alta calidad con Weasyprint.
* **`/mapa-conceptual <tema>`**: Genera un esquema conceptual con Graphviz (`.png`) y lo optimiza para el Aula Virtual.

---

## 🗂️ Estructura de Trabajo (`~/trabajo`)

* **`01-unidades-html/`**: Plantillas de lecciones HTML, `estilos-educamadrid.css` y validador `limpiar_html_moodle.py`.
* **`02-cuestionarios-moodle/`**: Bancos de preguntas en formato **GIFT** y **Moodle XML**, y validador `generador_gift.py`.
* **`03-fichas-y-tareas-docs/`**: Guías docentes, rúbricas LOMLOE y conversor `exportar_a_docx.py`.
* **`04-material-multimedia/`**: Compilador de esquemas Graphviz (`generar_diagrama.py`) y compresor (`optimizar_imagen.py`).
* **`05-herramientas-pdf/`**: Extractor de currículos/libros en PDF (`extractor_texto_pdf.py`) y compilador (`generar_pdf_apuntes.py`).

---

## 🔒 Credenciales del Sistema

* **Usuario**: `docente` (o `alumno`) | **Contraseña**: `docente` (o `alumno`)
* **Permisos**: Administrador con `sudo` sin contraseña
* **Puertos (NAT)**: `49374` (OpenCode GUI), `8080 ➔ 80` (Gestor de Archivos y Vista Previa), `2222 ➔ 22` (SSH)
