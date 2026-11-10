#!/usr/bin/env python3
# =============================================================
#  descifrar.py - Descifra la passphrase de rega_town (Rega's Town)
#  Proyecto 2 - IC-8071 Seguridad del Software (ITCR)
#
#  IDEA GENERAL:
#  La validacion del binario tiene 2 etapas:
#    1) 9 regex que fijan casi toda la bandera ("la rejilla" de 33 chars).
#    2) check_input: multiplica los codigos ASCII de 7 pedazos de la
#       passphrase y los compara contra 7 constantes (corr_values) que
#       sacamos de la pila con gdb (comando: x/14gx $rsp+0x180).
#
#  Este script hace fuerza bruta INTELIGENTE: para cada pedazo solo
#  prueba las combinaciones que las regex permiten y se queda con las
#  que el producto de los ord() coincide con la constante objetivo.
# =============================================================

# --- Alfabetos candidatos, sacados de la rejilla (las 9 regex) ---
DIGITOS    = "0123456789"
MAYUSCULAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MINUSCULAS = "abcdefghijklmnopqrstuvwxyz"
LETRAS     = MAYUSCULAS + MINUSCULAS
RANGO_N_X  = "nopqrstuvwxyz"            # regex 8: [n-x]
RANGO_A_H  = "abcdefgh"                # regex 9: [a-h]


def producto(texto):
    """Multiplica los codigos ASCII de los caracteres de un string.
    Ejemplo: producto('O7') = ord('O') * ord('7') = 79 * 55 = 4345."""
    resultado = 1
    for caracter in texto:
        resultado = resultado * ord(caracter)
    return resultado


# ---- Las 7 "palabras": una funcion por pedazo de la passphrase ----

def palabra_1(objetivo):
    """Posiciones 4-6: [X-Z], un digito, y una letra cualquiera (regex 8)."""
    encontradas = list()
    for c1 in "XYZ":
        for c2 in DIGITOS:
            for c3 in LETRAS:
                palabra = c1 + c2 + c3
                if producto(palabra) == objetivo:
                    encontradas.append(palabra)
    return encontradas


def palabra_2(objetivo):
    """Posiciones 8-10: 'A' fija, un NO-digito (letra) y un digito (regex 8)."""
    encontradas = list()
    for c2 in LETRAS:
        for c3 in DIGITOS:
            palabra = "A" + c2 + c3
            if producto(palabra) == objetivo:
                encontradas.append(palabra)
    return encontradas


def palabra_3(objetivo):
    """Posiciones 12-14: 'T' fija, 'h' o '7', y un digito (regex 9).
    Nota: en [h|7] el '|' es literal adentro de los corchetes, no
    significa 'o'; por eso solo probamos h y 7."""
    encontradas = list()
    for c2 in "h7":
        for c3 in DIGITOS:
            palabra = "T" + c2 + c3
            if producto(palabra) == objetivo:
                encontradas.append(palabra)
    return encontradas


def palabra_4(objetivo):
    """Posiciones 16-19: una mayuscula, un digito, 'n' fija y [a-h] (regex 9)."""
    encontradas = list()
    for c1 in MAYUSCULAS:
        for c2 in DIGITOS:
            for c4 in RANGO_A_H:
                palabra = c1 + c2 + "n" + c4
                if producto(palabra) == objetivo:
                    encontradas.append(palabra)
    return encontradas


def palabra_5(objetivo):
    """Posiciones 21-22: 'O' fija y un digito (regex 9).
    Este era EL hueco que ninguna regex podia fijar: solo sabiamos
    que era un digito, y el producto nos lo revela."""
    encontradas = list()
    for c2 in DIGITOS:
        palabra = "O" + c2
        if producto(palabra) == objetivo:
            encontradas.append(palabra)
    return encontradas


def palabra_6(objetivo):
    """Posiciones 24-26: 'T' fija, una letra, y 'e' fija (regex 7 y 9)."""
    encontradas = list()
    for c2 in LETRAS:
        palabra = "T" + c2 + "e"
        if producto(palabra) == objetivo:
            encontradas.append(palabra)
    return encontradas


def palabra_7(objetivo):
    """Posiciones 28-31: 'T' fija, dos letras en [n-x], y 'n' o 'c' (regex 8)."""
    encontradas = list()
    for c2 in RANGO_N_X:
        for c3 in RANGO_N_X:
            for c4 in "nc":
                palabra = "T" + c2 + c3 + c4
                if producto(palabra) == objetivo:
                    encontradas.append(palabra)
    return encontradas


def pedir_decimal(mensaje):
    """Pide un numero al usuario y no avanza hasta que sea valido."""
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("Ese valor no es un numero entero, proba de nuevo.")


def main():
    print("=" * 60)
    print(" Descifrador de la passphrase - Rega's Town")
    print("=" * 60)
    print("Pone los 7 productos en DECIMAL, en el orden que salieron en gdb.")
    print("(Si los tenes en hexadecimal, pasalos primero por conversor.py)\n")

    # Pedimos los 7 objetivos (las constantes de corr_values en decimal)
    objetivos = list()
    for i in range(1, 8):
        objetivos.append(pedir_decimal(f"Producto de la palabra {i}: "))

    # Las 7 funciones, en orden. En Python las funciones son objetos
    # y se pueden guardar en listas.
    funciones = (palabra_1, palabra_2, palabra_3, palabra_4,
                 palabra_5, palabra_6, palabra_7)

    partes = list()   # aca vamos guardando la palabra elegida de cada pedazo

    # zip() recorre las dos listas a la vez: en cada vuelta nos da
    # la funcion y el objetivo que le toca, sin indexar nada.
    numero = 0
    for funcion, objetivo in zip(funciones, objetivos):
        numero = numero + 1
        candidatas = funcion(objetivo)
        print(f"\nPalabra {numero} -> candidatas: {candidatas}")

        if not candidatas:
            # No encontro ninguna: seguro el decimal estaba mal escrito
            print("   (!) Ninguna combinacion calza, revisa ese numero.")
            partes.append("???")
        elif len(candidatas) == 1:
            # Si solo hay una, se agrega sola
            partes = partes + candidatas
        else:
            # Mas de una combinacion multiplica igual al mismo numero:
            # hay que elegir la que se lee como palabra en leetspeak.
            eleccion = input("   Hay varias, escribi la correcta: ")
            while eleccion not in candidatas:
                eleccion = input("   Esa no esta, escribi una de las candidatas: ")
            partes.append(eleccion)

    # Armamos la passphrase: HTB{ + palabras separadas por guion bajo + }
    passphrase = "HTB{" + "_".join(partes) + "}"

    print("\n" + "=" * 60)
    print(" PASSPHRASE:")
    print(" " + passphrase)
    print(f" Largo: {len(passphrase)} caracteres (la regex 1 exige exactamente 33)")
    print("=" * 60)


if __name__ == "__main__":
    main()
