import socket

sock=socket.socket()
sock.bind(('', 9090))
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
