from flask import Flask, render_template
from flask_socketio import SocketIO, send
import os


app=Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)

@socketio.on('message')
def echo_socket(msg):
        send(msg, broadcast=True)

@app.route('/')
def index():
    return render_template("main.html")

if __name__ == "__main__":
    socketio.run(app)
