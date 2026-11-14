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
ENC = "b4e4e9ab09364ac2a514e53566c399145a34f118917d2370fab53dfa3de500d16915"  # 0x00100420
KEY = "fcb0abd06e442ba0c77d8b5239a7ad606e6b976aa1107c1bc9c753c951d070e50a26"  # 0x00100460


def main() -> None:
    flag = "".join(chr(a ^ b) for a, b in zip(bytes.fromhex(ENC), bytes.fromhex(KEY)))
    print(flag + "}")


if __name__ == "__main__":
    main()
