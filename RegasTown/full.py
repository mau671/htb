#!/usr/bin/env python3
"""
Rega's Town (HackTheBox)

    python3 full.py

check_input multiplica los codigos ASCII de los 7 segmentos de la
passphrase y los compara contra las constantes de corr_values.
La version completa (para practicar) es full_test.py.
"""

from itertools import product

# --- corr_values (en decimal) ------------------------------------------------
# Passphrase de prueba:
#   HTB{X0a_Aa0_Th0_A0na_O0_Tae_Tnnn}
#
#   (gdb) break rega_town::check_input
#   (gdb) run
#   (gdb) break *($pc+0x516)
#   (gdb) c
#   (gdb) x/14gx $rsp+0x180
CORR_VALUES = [???, ???, ???, ???, ???, ???, ???]

# --- alfabetos genericos (no son datos del reto) ----------------------------
DIGITOS    = "0123456789"
MAYUSCULAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MINUSCULAS = "abcdefghijklmnopqrstuvwxyz"
LETRAS     = MAYUSCULAS + MINUSCULAS

# --- la rejilla: cada segmento es la tupla de alfabetos que las regex
#     permiten por posicion (un caracter fijo es un alfabeto de 1 letra) -----
SEGMENTOS = [
    (???, DIGITOS, LETRAS),           # pos 4-6:   regex 8: [X-Z]\d?.\_A...
    (???, LETRAS, DIGITOS),           # pos 8-10:  regex 8: \_A\D\d
    (???, ???, DIGITOS),              # pos 12-14: regex 9: \_T[h|7]\d\_ (el | es literal)
    (MAYUSCULAS, DIGITOS, ???, ???),  # pos 16-19: regex 9: [[:upper:]]\dn[a-h]\_
    (???, DIGITOS),                   # pos 21-22: regex 9: \_[O]\d\_ (EL hueco de la rejilla)
    (???, LETRAS, ???),               # pos 24-26: regex 7: .{24}T.e.T
    (???, ???, ???, ???),             # pos 28-31: regex 8: T[n-x]{2}[n|c]
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
