# OpenCode v2 - Cliente GUI Portable para Windows

Aplicación de escritorio **portable (sin instalación)** para conectar docentes con el agente de IA **OpenCode v2** que se ejecuta dentro de la máquina virtual **ArchLinux-EducaMadrid**.

---

## 🚀 Uso Rápido (1 Clic)

1. **Inicia la máquina virtual** en VirtualBox:
   * Selecciona `ArchLinux-EducaMadrid` y pulsa **Iniciar** (modo normal o desatendido/iniciar en segundo plano).
2. **Ejecuta la aplicación:**
   * Haz doble clic en `OpenCode-EducaMadrid.exe` (o `Iniciar-OpenCode.bat`).
3. **¡Listo!**
   * La aplicación comprobará automáticamente si la máquina virtual está lista.
   * Si la máquina aún está arrancando, mostrará una ventana de espera y reintentará automáticamente.
   * En cuanto el servicio esté listo, se abrirá la interfaz de OpenCode v2 en una ventana de aplicación independiente (sin barras de navegación ni pestañas).

---

## ⚙️ Características

- **100% Portable:** No requiere instalación, ni permisos de administrador, ni NodeJS, ni Python en tu Windows.
- **Conexión Totalmente Automática:** Detecta el puerto reenviado por VirtualBox (`127.0.0.1:49374`) y autentica automáticamente la sesión.
- **Ventana de Aplicación Nativa:** Se ejecuta en modo ventana independiente (`--app mode`), con su propio icono en la barra de tareas y sin mezclar pestañas personales.
- **Perfil Aislado:** Mantiene el historial de chats, preferencias de tema (oscuro/claro) y configuración en un perfil aislado en tu equipo.
- **Control de Espera y Reconexión:** Si abres la aplicación antes de que la máquina virtual termine de arrancar, la app espera activamente a la VM. Si la VM no está encendida, te avisa con un diálogo claro de reintento.

---

## 🔒 Parámetros de Conexión

- **Host:** `127.0.0.1` (localhost mediante NAT de VirtualBox)
- **Puerto:** `49374`
- **Token de Acceso:** Preconfigurado automáticamente (`educamadrid`)
