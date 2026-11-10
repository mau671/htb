#!/usr/bin/env python3
print("=== Conversor hexadecimal -> decimal (escribi 'q' para salir) ===")

while True:
    # Pedimos el valor hexadecimal (ej: 0x7a070)
    hexa = input("\nHexadecimal: ")

    # Opcion de salida
    if hexa.lower() in ("q", "quit", "salir"):
        print("Chao!")
        break

    try:
        # int(texto, 16) convierte un string en base 16 a entero decimal.
        # Python acepta el valor con o sin el prefijo 0x.
        decimal = int(hexa, 16)
        print(f"{hexa} = {decimal}")
    except ValueError:
        # Si no es un hexadecimal valido, avisamos y volvemos a pedir
        print("Ese valor no es un hexadecimal valido, proba de nuevo.")
