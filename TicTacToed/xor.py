#!/usr/bin/env python3
import sys
import hashlib

if len(sys.argv) != 4:
    print(f"Uso: python3 {sys.argv[0]} <hex_part1> <hex_part2> <hex_part3>")
    sys.exit(1)

parts_hex = sys.argv[1:4]
decrypted_parts = []

for idx, hex_str in enumerate(parts_hex, 1):
    raw_bytes = bytes.fromhex(hex_str)
    text = ''.join(chr(b ^ 0x5a) for b in raw_bytes)
    print(f"  Parte {idx} ({hex_str}) ^ 0x5A = {text}")
    decrypted_parts.append(text)

access_code = ''.join(decrypted_parts)
hash_calc = hashlib.sha256(access_code.encode()).hexdigest()

print("\n[+] Clave reconstruida:")
print(f"  Access Code : {access_code}")
print(f"  SHA-256     : {hash_calc}")
