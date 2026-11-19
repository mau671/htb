#!/usr/bin/env python3
"""
SEPC (HackTheBox)

    python3 full.py

El módulo checker.ko compara cada byte enviado contra ENC[i] ^ KEY[i], y los
dos blobs están juntos en .rodata: el XOR de ambos es la clave. Solo compara
0x22 = 34 bytes, así que la llave de cierre ('}') no entra en el cálculo y se
añade al final.
"""

# --- blobs de .rodata de checker.ko ---------------------------------------
ENC = "???"  # 0x00100420
KEY = "???"  # 0x00100460


def main() -> None:
    flag = "".join(chr(a ^ b) for a, b in zip(bytes.fromhex(ENC), bytes.fromhex(KEY)))
    print(flag + "}")


if __name__ == "__main__":
    main()
