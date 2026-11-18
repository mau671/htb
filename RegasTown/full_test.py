#!/usr/bin/env python3
"""
Rega's Town (HackTheBox)

    python3 full_test.py

Igual que full.py pero con todo ya puesto.
"""

from itertools import product

# --- corr_values: las 7 constantes en DECIMAL, en el orden del dump --------
# hex (como salen en gdb): 0x7a070, 0x5c436, 0x6cc60, 0x27b5776,
#                          0x10f9, 0xd76a0, 0x7465a58
CORR_VALUES = [
    499824,      # 1: posiciones 4-6
    377910,      # 2: posiciones 8-10
    445536,      # 3: posiciones 12-14
    41637750,    # 4: posiciones 16-19
    4345,        # 5: posiciones 21-22
    882336,      # 6: posiciones 24-26
    122051160,   # 7: posiciones 28-31
]

# --- alfabetos genericos (no son datos del reto) ----------------------------
DIGITOS    = "0123456789"
MAYUSCULAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MINUSCULAS = "abcdefghijklmnopqrstuvwxyz"
LETRAS     = MAYUSCULAS + MINUSCULAS

# --- la rejilla: cada segmento es la tupla de alfabetos que las regex
#     permiten por posicion (un caracter fijo es un alfabeto de 1 letra) -----
SEGMENTOS = [
    ("XYZ", DIGITOS, LETRAS),                      # pos 4-6
    ("A", LETRAS, DIGITOS),                        # pos 8-10
    ("T", "h7", DIGITOS),                          # pos 12-14
    (MAYUSCULAS, DIGITOS, "n", "abcdefgh"),        # pos 16-19
    ("O", DIGITOS),                                # pos 21-22
    ("T", LETRAS, "e"),                            # pos 24-26
    ("T", "nopqrstuvwxyz", "nopqrstuvwxyz", "nc"), # pos 28-31
]


def producto(texto):
    """Multiplica los codigos ASCII de los caracteres de un string.
    Ejemplo: producto('O7') = ord('O') * ord('7') = 79 * 55 = 4345."""
    resultado = 1
    for caracter in texto:
        resultado *= ord(caracter)
    return resultado


# El producto ASCII no es inyectivo: hay combinaciones distintas que
# multiplican igual (colisiones), y el binario acepta varias passphrase.
# Por eso resolver() devuelve TODAS las candidatas y es uno quien elige
# la que se lee como frase en leetspeak.


def resolver(objetivo, alfabetos):
    """Fuerza bruta acotada por la rejilla: para cada segmento solo
    prueba las combinaciones que las regex permiten y se queda con las
    que el producto de los ord() coincide con la constante objetivo."""
    combinaciones = ("".join(p) for p in product(*alfabetos))
    candidatas = [c for c in combinaciones if producto(c) == objetivo]
    if not candidatas:
        raise SystemExit(f"[!] Ninguna combinacion calza con {objetivo}: "
                         "revisa CORR_VALUES y la rejilla.")
    return candidatas


def main():
    print("=" * 60)
    print(" Descifrador de la passphrase - Rega's Town")
    print("=" * 60)

    partes = list()
    for numero, (objetivo, alfabetos) in enumerate(zip(CORR_VALUES, SEGMENTOS), 1):
        candidatas = resolver(objetivo, alfabetos)
        print(f"\nSegmento {numero} -> candidatas: {candidatas}")

        if len(candidatas) == 1:
            # Si solo hay una, se agrega sola
            partes += candidatas
        else:
            # Hay varias combinaciones que multiplican igual:
            # se elige la que se lee como palabra en leetspeak.
            eleccion = input("   Hay varias, escribi la correcta: ")
            while eleccion not in candidatas:
                eleccion = input("   Esa no esta, escribi una de las candidatas: ")
            partes.append(eleccion)

    # Armamos la passphrase: HTB{ + segmentos separados por guion bajo + }
    passphrase = "HTB{" + "_".join(partes) + "}"

    print("\n" + "=" * 60)
    print(" PASSPHRASE:")
    print(" " + passphrase)
    print("=" * 60)


if __name__ == "__main__":
    main()
