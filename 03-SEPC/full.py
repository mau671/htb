#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pwntools"]
# ///
"""
SEPC (HackTheBox)

    uv run full.py              # recupera el flag y lo verifica en QEMU
    uv run full.py --flag-only  # solo recupera el flag (no arranca QEMU)
    uv run full.py --help

El bloque '/// script' es metadata PEP 723: 'uv run' crea un entorno temporal
con pwntools y ejecuta el archivo, sin venv ni pip install.
"""

import argparse
import os

from pwn import context, process

# --- blobs de .rodata de checker.ko ---------------------------------------
# ENC: bloque cifrado de 34 bytes.   Direccion en Ghidra: 0x00100420
# KEY: clave XOR de 34 bytes.        Direccion en Ghidra: 0x00100460
# El handler de read calcula el caracter esperado con ENC[i] ^ KEY[i].
ENC = "b4e4e9ab09364ac2a514e53566c399145a34f118917d2370fab53dfa3de500d16915"
KEY = "fcb0abd06e442ba0c77d8b5239a7ad606e6b976aa1107c1bc9c753c951d070e50a26"

# El modulo compara 0x22 = 34 caracteres, asi que el XOR devuelve la flag sin
# la llave de cierre. Se anade aqui.
CLOSE = "}"

# --- entorno --------------------------------------------------------------
# Archivos del reto y comando de QEMU (equivale a run.sh).
KERNEL = "bzImage"
INITRD = "initramfs.cpio.gz"
QEMU = [
    "qemu-system-x86_64",
    "-kernel", KERNEL,
    "-initrd", INITRD,
    "--append", "console=ttyS0",
    "-nographic",
]


def recover_flag() -> str:
    """XOR byte a byte de los dos blobs -> flag completa."""
    flag = "".join(
        chr(a ^ b) for a, b in zip(bytes.fromhex(ENC), bytes.fromhex(KEY))
    )
    return flag if flag.endswith(CLOSE) else flag + CLOSE


def main() -> None:
    parser = argparse.ArgumentParser(description="Solver de SEPC.")
    parser.add_argument("--flag-only", action="store_true",
                        help="no arrancar QEMU, solo calcular el flag")
    parser.add_argument("--timeout", type=float, default=30.0,
                        help="segundos de espera al arranque de QEMU")
    args = parser.parse_args()

    flag = recover_flag()
    print(f"[+] FLAG: {flag}")

    if args.flag_only:
        return

    # El init del initramfs lanza /checker, que pide la clave por consola
    # serie y la envia byte a byte al modulo hasta validarla.
    io = process(QEMU, cwd=os.path.dirname(os.path.abspath(__file__)))

    io.recvuntil(b"offline verification", timeout=args.timeout)
    io.recvuntil(b"$ ", timeout=args.timeout)
    io.sendline(flag.encode())

    # Al validar, checker termina; como es el proceso init, el kernel entra
    # en panic ("Attempted to kill init"). Eso es normal y sirve de cierre.
    data = io.recvall(timeout=10)

    text = data.decode(errors="replace")
    io.close()

    if "PASSWORD VERIFIED" in text:
        io.success(f"verificado en QEMU: {flag}")
    else:
        io.failure("el flag no fue aceptado")
        print(text.strip() or "(sin salida)")


if __name__ == "__main__":
    context.log_level = "info"
    main()
