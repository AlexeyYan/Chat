from flask import Flask
import os
from flask_sockets import Sockets

app=Flask(__name__)
sockets=Sockets(app)

@sockets.route('/echo')
def echo_socket(ws):
    while not ws.closed:
        message=ws.recieve()
        ws.send(message)

@app.route('/')
def index():
    return 'Index page!'

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('',int(os.environ.get('PORT'))), app, handler_class = WebSocketHandler)
    server.serve_forever()
