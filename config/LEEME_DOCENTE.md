# 🏫 Bienvenido al Entorno de Creación de Contenidos EducaMadrid

Esta máquina virtual está diseñada para facilitar a los **docentes de la Comunidad de Madrid** la creación, adaptación y formateo de materiales educativos para sus **Aulas Virtuales (Moodle 4.x)**.

---

## 🚀 Inicio Rápido con OpenCode v2

El único agente de IA preinstalado en este sistema es **OpenCode v2**.

Para iniciar una sesión de trabajo con el asistente de creación de contenidos:

```bash
cd ~/trabajo
opencode
```

O si prefieres utilizar el modo servidor web de OpenCode v2 para trabajar desde el navegador de tu ordenador anfitrión:
```bash
opencode serve --port 49374
```
*(Luego abre en tu navegador del equipo anfitrión: `http://localhost:49374`)*

---

## 🗂️ Estructura de Trabajo (`~/trabajo`)

En tu carpeta de trabajo encontrarás plantillas y utilidades listas para usar:

* **`01-unidades-html/`**:
  * Plantillas de temas y lecciones en HTML con estilos adaptables compatibles con EducaMadrid.
  * `limpiar_html_moodle.py`: Script para limpiar HTML y garantizar compatibilidad con Moodle.
* **`02-cuestionarios-moodle/`**:
  * Bancos de preguntas en formato **GIFT** y **Moodle XML**.
  * `generador_gift.py`: Convierte tablas o listas de texto en preguntas tipo test listas para importar.
* **`03-fichas-y-tareas-docs/`**:
  * Modelos de guías docentes, enunciados de actividades y rúbricas de evaluación LOMLOE.
  * `exportar_a_docx.py`: Compilador rápido de Markdown a `.docx`.
* **`04-material-multimedia/`**:
  * Herramientas de optimización web de imágenes (`optimizar_imagen.py`).
  * Generación de mapas conceptuales y diagramas con Graphviz.
* **`05-herramientas-pdf/`**:
  * `extractor_texto_pdf.py`: Extrae texto y tablas de libros o temarios en PDF para que el agente trabaje con ellos.
  * Compilador de resúmenes y apuntes a PDF de alta resolución.

---

## 💡 Ejemplos de Peticiones para OpenCode v2

Pega directamente peticiones como estas en OpenCode:

1. **Crear una unidad didáctica en HTML**:
   > *"Crea una página HTML con el tema 'El ciclo del agua' para 1º de la ESO, usando cajas de aviso para conceptos clave, un desplegable con un ejercicio interactivo y una tabla resumen. Usa los estilos de `estilos-educamadrid.css`."*

2. **Generar un cuestionario para el Aula Virtual**:
   > *"A partir del archivo `apuntes.pdf` de la carpeta `05-herramientas-pdf`, genera un banco de 10 preguntas tipo test en formato GIFT con 4 opciones (1 correcta) y explicaciones en las retroalimentaciones. Guárdalo en `02-cuestionarios-moodle/examen_tema1.gift`."*

3. **Diseñar una rúbrica en Word (.docx)**:
   > *"Elabora una rúbrica de evaluación para una exposición oral de 4º de ESO con 4 niveles de desempeño (Insuficiente, Suficiente, Notable, Sobresaliente) según los criterios de comunicación lingüística. Guárdala como documento DOCX en `03-fichas-y-tareas-docs/`."*

4. **Optimizar imágenes para no saturar la cuota**:
   > *"Optimiza todas las imágenes de la carpeta `04-material-multimedia/` para que pesen menos de 300 KB y se vean nítidas en Moodle."*

---

## 🔒 Credenciales del Sistema

* **Usuario**: `docente` (o `alumno`)
* **Contraseña**: `docente` (o `alumno`)
* **Permisos**: Administrador con `sudo`
* **Acceso SSH desde el anfitrión**: `ssh -p 2222 docente@localhost`
