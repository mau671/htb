import os
from flask import Flask, Response, request, redirect

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))

@app.route('/', defaults={'path': ''}, methods=['GET', 'HEAD', 'POST'])
@app.route('/<path:path>', methods=['GET', 'HEAD', 'POST'])
def catch(path):
    print(f"[{request.method}] Path=/{path} Next-Action={request.headers.get('Next-Action')}")
    if request.method == 'HEAD':
        resp = Response("")
        resp.headers['Content-Type'] = 'text/x-component'
        return resp
    with open(os.path.join(BASE, 'destino.txt')) as f:
        destino = f.read().strip()
    print(f" -> redirigiendo a: {destino[:100]}...")
    return redirect(destino)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, threaded=True, debug=False)

