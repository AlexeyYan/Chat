import tornado.httpserver
import tornado.ioloop
import tornado.websocket
import tornado.web
import psycopg2
from hashlib import md5
import json
import time
import os

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    "static_url_prefix": "/static/",
}
con=(os.environ.get['DATABASE_URL'])
cur=con.cursor()
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        MainHandler.render(self,"templates/main.html")

class SocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()
    key=''
    def open(self):
        SocketHandler.clients.add(self)
        print("Client connected!")

    def check_origin(self, origin):
        return True

    def send(self, message):
        for client in SocketHandler.clients:
            client.write_message(json.dumps(message))

    def on_message(self, message):
        message=json.loads(message)
        if message['event']=='message':
            author=cur.execute("SELECT * FROM Users WHERE key={};".fomat(message['key'])).fetchone()
            if author!=None:
               msg={'event':'message', 'message':json.loads(message)['message'], 'author':author[1]}
               self.send(msg)
        elif message['event']=='alive':
            pass
        elif message['event']=='register':
            print(message)
            user=cur.execute("SELECT * FROM Users WHERE name={} AND passwd={};".format(message['name'], message['passwd'])).fetchone()
            if (user!=None):
              self.key=md5((user[2]+str(time.time()).encode)).hexdigest()
              cur.execute("UPDATE Users SET key={} WHERE name={};".format(self.key, user[1]))
              con.commit()
              msg={'event':'register', 'key':key, 'errors':[]}
              self.write_message(json.dumps(msg))
              print("User connected!")
              msg={'event':'connect', 'user':user[1]}
              self.send(msg)


    def on_close(self):
        SocketHandler.clients.remove(self)
        print("Connection closed")

application = tornado.web.Application([
    (r"/", SocketHandler),
    (r"/chat", MainHandler),
], **settings)

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(os.environ.get('PORT', 5000))
    tornado.ioloop.IOLoop.instance().start()
