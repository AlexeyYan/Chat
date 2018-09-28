from flask import Flask
from flas_socketio import SocketIO, send
import os


app=Flask(__name__)
app.config('SECRET_KEY') = 'mysecret'
socketio = SocketIO(app)

@socketio.on('message')
def echo_socket(msg):
        send(msg, broadcast=True)

@app.route('/')
def index():
    return 'Index page!'

if __name__ == "__main__":
    socketio.run(app)
