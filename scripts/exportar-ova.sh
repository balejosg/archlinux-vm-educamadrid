#!/usr/bin/env bash
# ==============================================================================
# EXPORTACIÓN OPTIMIZADA DE LA APPLIANCE VIRTUAL (.OVA) EDUCAMADRID
# ==============================================================================
set -euo pipefail

VM_NAME="ArchLinux-EducaMadrid"
OUTPUT_OVA="/home/run0/ArchLinux-EducaMadrid.ova"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 2222"

echo "======================================================================"
echo "📦 OPTIMIZANDO Y EXPORTANDO APPLIANCE .OVA (EDUCAMADRID)"
echo "======================================================================"

# Crear helper para contraseñas de SSH sin herramientas externas
cat << 'EOF' > /tmp/askpass_docente.sh
#!/bin/sh
echo "docente"
EOF
chmod +x /tmp/askpass_docente.sh

# 1. Comprobar si la VM está en ejecución
VM_STATE=$(VBoxManage showvminfo "${VM_NAME}" --machinereadable | grep "^VMState=" | cut -d'"' -f2)

if [ "${VM_STATE}" != "running" ]; then
    echo "▶️ Arrancando la máquina temporalmente para optimizar espacio..."
    VBoxManage startvm "${VM_NAME}" --type headless
    sleep 10
fi

# 2. Limpieza de cachés de paquetes y zero-fill para compresión máxima
echo "🧹 Limpiando cachés de paquetes, npm y rellenando espacio libre con ceros..."
SSH_ASKPASS=/tmp/askpass_docente.sh SSH_ASKPASS_REQUIRE=force setsid -w ssh $SSH_OPTS docente@127.0.0.1 \
    "echo docente | sudo -S bash -c 'rm -rf /var/cache/pacman/pkg/* /tmp/* /var/tmp/* /root/.cache/* /home/*/.cache/*; npm cache clean --force 2>/dev/null || true; cat /dev/zero > /zero.dat 2>/dev/null || true; rm -f /zero.dat; sync'" || true

# 3. Apagado limpio
echo "🛑 Apagando la máquina virtual..."
SSH_ASKPASS=/tmp/askpass_docente.sh SSH_ASKPASS_REQUIRE=force setsid -w ssh $SSH_OPTS docente@127.0.0.1 \
    "echo docente | sudo -S poweroff" || true

# Esperar a que se apague
while [ "$(VBoxManage showvminfo "${VM_NAME}" --machinereadable | grep '^VMState=' | cut -d'"' -f2)" = "running" ]; do
    echo "   Esperando apagado completo..."
    sleep 3
done

# 4. Exportar a OVA
echo "💾 Exportando appliance a ${OUTPUT_OVA}..."
rm -f "${OUTPUT_OVA}"
VBoxManage export "${VM_NAME}" -o "${OUTPUT_OVA}"

# 5. Calcular checksum SHA-256
echo "🔒 Calculando suma de verificación SHA-256..."
sha256sum "${OUTPUT_OVA}" > "${OUTPUT_OVA}.sha256"
cat "${OUTPUT_OVA}.sha256"

echo "======================================================================"
echo "✅ EXPORTACIÓN FINALIZADA CON ÉXITO: ${OUTPUT_OVA}"
echo "======================================================================"
