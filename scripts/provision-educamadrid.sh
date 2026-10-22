#!/usr/bin/env bash
# ==============================================================================
# Script de aprovisionamiento interno: Arch Linux VM (Edición Docente EducaMadrid)
# Se ejecuta dentro de la VM para configurar OpenCode v2 y herramientas didácticas
# ==============================================================================
set -euo pipefail

echo "======================================================================"
echo "🏫 APROVISIONANDO ENTORNO EDUCAMADRID (OPENCODE v2 - DOCENTES)"
echo "======================================================================"

# 1. Localización y Teclado Español
echo "[1/7] Configurando localización española (es_ES.UTF-8, KEYMAP=es)..."
sed -i 's/^#\(es_ES.UTF-8 UTF-8\)/\1/' /etc/locale.gen
sed -i 's/^#\(en_US.UTF-8 UTF-8\)/\1/' /etc/locale.gen
locale-gen

cat << 'EOF' > /etc/locale.conf
LANG=es_ES.UTF-8
LC_COLLATE=C
EOF

cat << 'EOF' > /etc/vconsole.conf
KEYMAP=es
FONT=eurlatgr
EOF

ln -sf /usr/share/zoneinfo/Europe/Madrid /etc/localtime
timedatectl set-timezone Europe/Madrid 2>/dev/null || true

# Configurar mirrors rápidos y descargas paralelas para evitar timeouts
cat << 'EOF' > /etc/pacman.d/mirrorlist
Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch
Server = https://mirror.osbeck.com/archlinux/$repo/os/$arch
Server = https://mirror.raiolanetworks.com/archlinux/$repo/os/$arch
Server = https://mirror.dkm.cz/archlinux/$repo/os/$arch
Server = https://fastly.mirror.pkgbuild.com/$repo/os/$arch
EOF
sed -i 's/^#ParallelDownloads = 5/ParallelDownloads = 5/' /etc/pacman.conf

# 2. Desinstalar componentes innecesarios (Java, Sysadmin, Sostenibilidad, Tutor Socrático)
echo "[2/7] Limpiando dependencias no requeridas (Java, Docker, MQTT, PowerTOP)..."
systemctl stop docker.service 2>/dev/null || true
systemctl disable docker.service 2>/dev/null || true
systemctl stop mosquitto.service 2>/dev/null || true
systemctl disable mosquitto.service 2>/dev/null || true

# Eliminar paquetes si están instalados (sin fallar si no existen)
pacman -Rdd --noconfirm jdk-openjdk openjdk-src maven mosquitto powertop scaphandre docker docker-compose 2>/dev/null || true

# 3. Instalación de paquetes oficiales para Documentos, Imágenes y HTML
echo "[3/7] Instalando herramientas de procesamiento de Documentos, Imágenes y HTML..."
pacman -Sy --noconfirm --needed \
    base-devel git curl wget rsync jq vim nano tmux zsh \
    ripgrep fd tree htop \
    nodejs npm \
    pandoc \
    poppler \
    imagemagick optipng jpegoptim \
    graphviz \
    libreoffice-fresh \
    ttf-dejavu ttf-liberation noto-fonts \
    python python-pip python-virtualenv \
    python-pillow python-matplotlib python-requests

# 4. Instalación de librerías Python especializadas en Educación y Formatos
echo "[4/7] Instalando librerías Python para DOCX, PDF, HTML y Moodle..."
pip install --break-system-packages --upgrade \
    python-docx \
    pypdf pdfplumber pymupdf \
    weasyprint \
    beautifulsoup4 html5lib \
    openpyxl \
    markdown markdown-it-py

# 5. Instalación de OPENCODE v2 (Único programa de agentes)
echo "[5/7] Instalando OpenCode v2..."
# Intentar vía instalador oficial v2
export VERSION="2.1.2"
curl -fsSL https://opencode.ai/v2/install | bash || true

# Como respaldo o para asegurar binario global en /usr/local/bin:
if ! command -v opencode >/dev/null 2>&1; then
    npm install -g @opencode/cli@latest || true
fi

# Verificar ubicación de binario
if [ -f /root/.opencode/bin/opencode ] && [ ! -f /usr/local/bin/opencode ]; then
    cp /root/.opencode/bin/opencode /usr/local/bin/opencode
    chmod 755 /usr/local/bin/opencode
fi

echo "✓ Versión instalada de OpenCode:"
opencode --version 2>&1 || true

# 6. Configuración de usuarios: 'docente' y 'alumno'
echo "[6/7] Configurando cuentas de usuario ('docente' y 'alumno')..."
for USUARIO in docente alumno; do
    if ! id -u "$USUARIO" >/dev/null 2>&1; then
        useradd -m -s /bin/bash -G wheel "$USUARIO"
    fi
    echo "${USUARIO}:${USUARIO}" | chpasswd
    
    # Soporte VirtualBox Guest Additions
    usermod -aG vboxsf "$USUARIO" 2>/dev/null || true
    
    U_HOME="/home/${USUARIO}"
    mkdir -p "${U_HOME}/.config/opencode"
    mkdir -p "${U_HOME}/trabajo"
    
    # Copiar configuración de OpenCode v2
    if [ -f /tmp/opencode.json ]; then
        cp /tmp/opencode.json "${U_HOME}/.config/opencode/opencode.json"
    fi
    if [ -f /tmp/AGENTS.md ]; then
        cp /tmp/AGENTS.md "${U_HOME}/.config/opencode/AGENTS.md"
        cp /tmp/AGENTS.md "${U_HOME}/trabajo/AGENTS.md"
    fi
    if [ -f /tmp/LEEME_DOCENTE.md ]; then
        cp /tmp/LEEME_DOCENTE.md "${U_HOME}/trabajo/LEEME.md"
        cp /tmp/LEEME_DOCENTE.md "${U_HOME}/LEEME.md"
    fi

    # Copiar plantillas docentes
    if [ -d /tmp/plantillas-educamadrid ]; then
        cp -r /tmp/plantillas-educamadrid/* "${U_HOME}/trabajo/"
    fi
    
    chown -R "${USUARIO}:${USUARIO}" "${U_HOME}"
done

# Configurar sudoers para que wheel no requiera contraseña
cat << 'EOF' > /etc/sudoers.d/10-wheel-nopasswd
%wheel ALL=(ALL) NOPASSWD: ALL
EOF
chmod 0440 /etc/sudoers.d/10-wheel-nopasswd

# 7. Servicios del Sistema y Additions
echo "[7/7] Habilitando servicios del sistema..."
pacman -S --noconfirm --needed virtualbox-guest-utils 2>/dev/null || true
systemctl enable vboxservice.service 2>/dev/null || true
systemctl enable sshd.service 2>/dev/null || true
systemctl start sshd.service 2>/dev/null || true

echo "======================================================================"
echo "✅ APROVISIONAMIENTO EDUCAMADRID COMPLETADO CON ÉXITO"
echo "======================================================================"
