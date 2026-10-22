#!/usr/bin/env bash
# ==============================================================================
# CREACIÓN Y CONFIGURACIÓN AUTOMATIZADA: Arch Linux VM (Docente EducaMadrid)
# ==============================================================================
set -euo pipefail

VM_NAME="ArchLinux-EducaMadrid"
BASE_OVA="/tmp/ArchLinux-base.ova"
PROJECT_DIR="/home/run0/archlinux-vm-educamadrid"

echo "======================================================================"
echo "🚀 CONSTRUCCIÓN DE LA VM ARCH LINUX (DOCENTES EDUCAMADRID - OPENCODE v2)"
echo "======================================================================"

# 1. Comprobar dependencias del host
for cmd in VBoxManage curl ssh scp; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "❌ Falta herramienta en host: $cmd"
        exit 1
    fi
done

# 2. Verificar existencia del OVA base
if [ ! -f "${BASE_OVA}" ]; then
    echo "📥 Descargando imagen base ArchLinux.ova..."
    curl -L -C - --retry 5 --retry-delay 2 -o "${BASE_OVA}" \
        "https://github.com/balejosg/archlinux-vm/releases/download/v1.3.0/ArchLinux.ova"
fi

# 3. Eliminar VM previa con el mismo nombre si existe
if VBoxManage showvminfo "${VM_NAME}" >/dev/null 2>&1; then
    echo "⚠️ Eliminando versión anterior de ${VM_NAME}..."
    VBoxManage controlvm "${VM_NAME}" poweroff 2>/dev/null || true
    sleep 2
    VBoxManage unregistervm "${VM_NAME}" --delete || true
fi

# 4. Importar base OVA
echo "🔄 Importando OVA base como '${VM_NAME}'..."
VBoxManage import "${BASE_OVA}" --vsys 0 --vmname "${VM_NAME}"

# 5. Configurar hardware y reenvío de puertos (NAT)
echo "⚙️ Configurando puertos y hardware de '${VM_NAME}'..."
VBoxManage modifyvm "${VM_NAME}" \
    --cpus 2 \
    --memory 4096 \
    --vram 64 \
    --graphicscontroller vmsvga \
    --audio-enabled off

# Limpiar reglas NAT anteriores y añadir las de EducaMadrid
VBoxManage modifyvm "${VM_NAME}" --natpf1 delete "guestssh" 2>/dev/null || true
VBoxManage modifyvm "${VM_NAME}" --natpf1 delete "ssh" 2>/dev/null || true
VBoxManage modifyvm "${VM_NAME}" --natpf1 delete "web" 2>/dev/null || true
VBoxManage modifyvm "${VM_NAME}" --natpf1 delete "opencode" 2>/dev/null || true

VBoxManage modifyvm "${VM_NAME}" \
    --natpf1 "ssh,tcp,127.0.0.1,2222,,22" \
    --natpf1 "web,tcp,127.0.0.1,8080,,80" \
    --natpf1 "opencode,tcp,127.0.0.1,49374,,49374"

# 6. Iniciar la máquina virtual en modo headless
echo "▶️ Iniciando '${VM_NAME}' (headless)..."
VBoxManage startvm "${VM_NAME}" --type headless

# Crear helper para contraseñas de SSH sin herramientas externas
cat << 'EOF' > /tmp/askpass_alumno.sh
#!/bin/sh
echo "alumno"
EOF
chmod +x /tmp/askpass_alumno.sh

# Esperar a que el servidor SSH responda
echo "⏳ Esperando a que el puerto SSH (2222) esté listo..."
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=3 -p 2222"
MAX_ATTEMPTS=30
ATTEMPT=1
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if SSH_ASKPASS=/tmp/askpass_alumno.sh SSH_ASKPASS_REQUIRE=force setsid -w ssh $SSH_OPTS alumno@127.0.0.1 "echo ok" >/dev/null 2>&1; then
        echo "✓ Conexión SSH establecida con éxito en el intento $ATTEMPT."
        break
    fi
    echo "   Intento $ATTEMPT/$MAX_ATTEMPTS... esperando 3s"
    sleep 3
    ATTEMPT=$((ATTEMPT + 1))
done

if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
    echo "❌ No se pudo conectar a la VM por SSH en el puerto 2222."
    exit 1
fi

# 7. Transferir archivos de aprovisionamiento
echo "📦 Copiando configuración y plantillas a la máquina virtual..."
SSH_ASKPASS=/tmp/askpass_alumno.sh SSH_ASKPASS_REQUIRE=force setsid -w scp -P 2222 -r \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    "${PROJECT_DIR}/config/AGENTS.md" \
    "${PROJECT_DIR}/config/opencode.json" \
    "${PROJECT_DIR}/config/LEEME_DOCENTE.md" \
    "${PROJECT_DIR}/config/opencode-gateway.mjs" \
    "${PROJECT_DIR}/config/educamadrid-files.py" \
    "${PROJECT_DIR}/plantillas-educamadrid" \
    "${PROJECT_DIR}/scripts/provision-educamadrid.sh" \
    alumno@127.0.0.1:/tmp/

# 8. Ejecutar script de aprovisionamiento como root
echo "🔧 Ejecutando aprovisionamiento interno (OpenCode v2, Documentos, Moodle)..."
SSH_ASKPASS=/tmp/askpass_alumno.sh SSH_ASKPASS_REQUIRE=force setsid -w ssh $SSH_OPTS alumno@127.0.0.1 \
    "echo alumno | sudo -S bash /tmp/provision-educamadrid.sh"

echo "======================================================================"
echo "🎉 VM ARCH LINUX EDUCAMADRID LISTA Y OPERATIVA"
echo "======================================================================"
