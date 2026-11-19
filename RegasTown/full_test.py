#!/usr/bin/env python3
"""
Rega's Town (HackTheBox)

    python3 full_test.py
"""

import re
from itertools import product

# --- regex embebidas: strings bin/rega_town | grep '(?:' --------------------
REGEX = r"^.{33}$(?:^[\x48][\x54][\x42]).*^.{3}(\x7b).*(\x7d)$^[[:upper:]]{3}.[[:upper:]].{3}[[:upper:]].{3}[[:upper:]].{3}[[:upper:]].{4}[[:upper:]].{2}[[:upper:]].{3}[[:upper:]].{4}$(?:.*\x5f.*)(?:.[^0-9]*\d.*){5}.{24}\x54.\x65.\x54.*^.{4}[X-Z]\d._[A]\D\d.................[[:upper:]][n-x]{2}[n|c].$.{11}_T[h|7]\d_[[:upper:]]\dn[a-h]_[O]\d_[[:alpha:]]{3}_.{5}"

# --- corr_values: las 7 constantes, tal cual salen de Ghidra ----------------
CORR_VALUES = [
    0x7a070,
    0x5c436,
    0x6cc60,
    0x27b5776,
    0x10f9,
    0xd76a0,
    0x7465a58,
]

# --- alfabetos --------------------------------------------------------------
MAYUSCULAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MINUSCULAS = "abcdefghijklmnopqrstuvwxyz"
DIGITOS    = "0123456789"
LETRAS     = MAYUSCULAS + MINUSCULAS
UNIVERSO   = LETRAS + DIGITOS + "_{}"

POSIX = {
    "[[:upper:]]": MAYUSCULAS,
    "[[:lower:]]": MINUSCULAS,
    "[[:alpha:]]": LETRAS,
    "[[:digit:]]": DIGITOS,
}

# token de una regex: clase POSIX, clase, grupo, cuantificador, escape o literal
TOKEN = re.compile(r"\[\[:[a-z]+:\]\]|\[[^\]]*\]|\(\?:|\(|\)|\{\d+\}|\*|\+|\?|\^|\$|\.|\\[dDwW]|\\x[0-9a-fA-F]{2}|.", re.S)

# los 7 pedazos de la passphrase: posiciones 4-31 entre los guiones bajos
TROZOS = ((4, 7), (8, 11), (12, 15), (16, 20), (21, 23), (24, 27), (28, 32))


def expandir_clase(clase):
    """[X-Z] -> 'XYZ'; [a-h] -> 'abcdefgh'; [h|7] -> 'h7'."""
    contenido = clase[1:-1]
    salida = ""
    i = 0
    while i < len(contenido):
        if contenido.startswith(r"\x", i):
            salida += chr(int(contenido[i + 2:i + 4], 16))
            i += 4
        elif i + 2 < len(contenido) and contenido[i + 1] == "-":
            salida += "".join(chr(c) for c in range(ord(contenido[i]), ord(contenido[i + 2]) + 1))
            i += 3
        else:
            if contenido[i] != "|":  # el | adentro de una clase es literal
                salida += contenido[i]
            i += 1
    return salida


def dividir_regex(blob):
    """Parte el blob concatenado en las regex individuales."""
    unidades, actual = [], []
    profundidad = 0
    tokens = TOKEN.findall(blob)
    i = 0
    while i < len(tokens):
        t = tokens[i]
        actual.append(t)
        sigue = tokens[i + 1] if i + 1 < len(tokens) else None
        if t in ("(", "(?:"):
            profundidad += 1
        elif t == ")":
            profundidad -= 1
            if profundidad == 0:
                if sigue and sigue.startswith("{"):
                    actual.append(sigue)
                    i += 1
                    unidades.append(actual)
                    actual = []
                elif sigue in (None, "^", "(?:"):
                    unidades.append(actual)
                    actual = []
        elif t == "$" and profundidad == 0:
            unidades.append(actual)
            actual = []
        elif t == "*" and profundidad == 0 and len(actual) >= 2 and actual[-2] == ".":
            if sigue in (None, "^", "(?:", "."):
                unidades.append(actual)
                actual = []
        i += 1
    if actual:
        unidades.append(actual)
    return unidades


def restricciones(tokens):
    """Alfabetos por posicion de una regex; None si no es de largo fijo."""
    posicion = 0
    salida = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        i += 1
        if t in ("^", "$", "(", "(?:", ")"):
            continue
        if t in ("*", "+", "?"):
            return None
        if t == ".":
            if i < len(tokens) and tokens[i] == "*":
                break  # resto comodin: se acaba la parte fija
            conjunto = UNIVERSO
        elif t == r"\d":
            conjunto = DIGITOS
        elif t == r"\D":
            conjunto = LETRAS
        elif t.startswith(r"\x"):
            conjunto = chr(int(t[2:], 16))
        elif t in POSIX:
            conjunto = POSIX[t]
        elif t.startswith("["):
            conjunto = expandir_clase(t)
        else:
            conjunto = t
        veces = 1
        if i < len(tokens) and tokens[i].startswith("{"):
            veces = int(tokens[i][1:-1])
            i += 1
        for _ in range(veces):
            salida.append(conjunto)
            posicion += 1
    return salida


def derivar(blob):
    """Rejilla de 33 alfabetos a partir del blob de regex."""
    blob = blob.replace("\\\\", "\\")  # tolera el pegado con doble barra
    rejilla = [UNIVERSO] * 33
    for tokens in dividir_regex(blob):
        rest = restricciones(tokens)
        if rest is None:
            continue
        for pos, conjunto in enumerate(rest):
            permitido = set(rejilla[pos]) & set(conjunto)
            if conjunto == UNIVERSO:
                # "cualquiera" no reordena; solo recorta
                rejilla[pos] = "".join(c for c in rejilla[pos] if c in permitido)
            else:
                rejilla[pos] = "".join(c for c in conjunto if c in permitido)
    # "cualquiera" se acota a letras para la fuerza bruta
    rejilla = [LETRAS if conjunto == UNIVERSO else conjunto for conjunto in rejilla]
    for pos, conjunto in enumerate(rejilla):
        if not conjunto:
            raise SystemExit(f"[!] Rejilla vacia en la posicion {pos}: revisa REGEX.")
    return rejilla


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
        raise SystemExit(f"[!] Ninguna combinacion calza con {objetivo:#x}: "
                         "revisa CORR_VALUES.")
    return candidatas


def main():
    print("=" * 60)
    print(" Descifrador de la passphrase - Rega's Town")
    print("=" * 60)

    rejilla = derivar(REGEX)
    segmentos = [tuple(rejilla[p] for p in range(a, b)) for a, b in TROZOS]
    print(" Rejilla derivada de las regex:")
    for numero, alfabetos in enumerate(segmentos, 1):
        print(f"   {numero} -> {alfabetos}")

    # las constantes se pegan tal cual de Ghidra (0x...); si vienen como texto
    objetivos = [v if isinstance(v, int) else int(v, 16) for v in CORR_VALUES]

    partes = list()
    for numero, (objetivo, alfabetos) in enumerate(zip(objetivos, segmentos), 1):
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
