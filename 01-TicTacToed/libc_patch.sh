#!/usr/bin/env bash
# ==============================================================================
# libc_patch.sh
#
# Script de preparación de entorno para la ejecución del binario 'tictactoe'.
#
# Funcionamiento:
# 1. Verifica la presencia del binario objetivo 'tictactoe'.
# 2. Descarga el paquete libc6 versión 2.39 (Ubuntu 24.04 noble) si no existe.
# 3. Extrae las bibliotecas y el cargador dinámico (ld-linux-x86-64.so.2) en
#    un directorio local (~/glibc239/root) sin afectar la glibc del sistema.
# 4. Modifica las cabeceras ELF del binario usando 'patchelf':
#    - PT_INTERP (--set-interpreter): redirige el cargador dinámico a ld 2.39.
#    - DT_RUNPATH (--set-rpath): define la ruta de búsqueda de bibliotecas a la
#      carpeta extraída con libc 2.39.
# 5. Permite ejecutar './tictactoe' directamente sin requerir variables de entorno
#    (como LD_LIBRARY_PATH) ni llamadas explícitas al cargador.
# ==============================================================================

set -euo pipefail

TARGET_BIN="${1:-./tictactoe}"
GLIBC_DIR="${HOME}/glibc239"
DEB_URL="http://archive.ubuntu.com/ubuntu/pool/main/g/glibc/libc6_2.39-0ubuntu8_amd64.deb"
DEB_FILE="/tmp/libc6_2.39-0ubuntu8_amd64.deb"

# 1. Comprobación del binario objetivo
if [[ ! -f "$TARGET_BIN" ]]; then
    echo "[-] Error: no se encontro el binario objetivo: $TARGET_BIN" >&2
    exit 1
fi

# 2. Descarga de libc6 2.39 si no existe previamente
if [[ ! -f "$DEB_FILE" ]]; then
    echo "[*] Descargando paquete libc6 2.39..."
    wget -q -O "$DEB_FILE" "$DEB_URL"
fi

# 3. Extracción del cargador y bibliotecas en ruta local
if [[ -f "${GLIBC_DIR}/root/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2" ]]; then
    LOADER="${GLIBC_DIR}/root/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2"
    LIB_DIR="${GLIBC_DIR}/root/usr/lib/x86_64-linux-gnu"
elif [[ -f "${GLIBC_DIR}/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2" ]]; then
    LOADER="${GLIBC_DIR}/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2"
    LIB_DIR="${GLIBC_DIR}/usr/lib/x86_64-linux-gnu"
else
    echo "[*] Extrayendo bibliotecas y cargador en $GLIBC_DIR..."
    mkdir -p "$GLIBC_DIR"
    dpkg-deb -x "$DEB_FILE" "$GLIBC_DIR"
    LOADER="${GLIBC_DIR}/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2"
    LIB_DIR="${GLIBC_DIR}/usr/lib/x86_64-linux-gnu"
fi

# 4. Verificación de la herramienta patchelf
if ! command -v patchelf >/dev/null 2>&1; then
    echo "[-] Error: 'patchelf' no esta instalado. Instalar con: sudo apt-get install -y patchelf" >&2
    exit 1
fi

# 5. Respaldo del binario original si no existe
if [[ ! -f "${TARGET_BIN}.bak" ]]; then
    echo "[*] Creando respaldo en ${TARGET_BIN}.bak..."
    cp "$TARGET_BIN" "${TARGET_BIN}.bak"
fi

# 6. Modificación de cabeceras ELF (intérprete y RUNPATH)
echo "[*] Parcheando cabeceras ELF de $TARGET_BIN..."
patchelf --set-interpreter "$LOADER" \
         --set-rpath "$LIB_DIR" \
         "$TARGET_BIN"

# 7. Verificación final de cabeceras incrustadas
echo "[+] Parche completado exitosamente."
echo "    Interprete incrustado : $(readelf -l "$TARGET_BIN" | grep -o '/.*ld-linux.*so[0-9.]*' | head -1)"
echo "    RUNPATH incrustado    : $(readelf -d "$TARGET_BIN" | grep -o 'RUNPATH.*' | head -1)"
