import socket
import os

sock=socket.socket()
sock.bind(('', os.environ.get('PORT')))
sock.listen(1)
conn, addr = sock.accept()
print('connected', addr, conn)
while True:
    data = conn.recv(1024)
    if not data:
        break
    data=data.decode("utf-8").upper()
    conn.send(data.encode("utf-8"))

conn.close()
