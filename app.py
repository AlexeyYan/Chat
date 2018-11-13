from hashlib import md5
import tornado.httpserver
import tornado.ioloop
import tornado.websocket
import tornado.web
from db_handler import db, loginUser, registerUser, newMessage, getMessages
from datetime import datetime
import json
import time
import os


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    "static_url_prefix": "/static/",
}
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        MainHandler.render(self,"templates/main.html")

class SocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()
    key=''
    def open(self):
        print("Client connected!")

    def check_origin(self, origin):
        return True

    def send(self, message):
        for client in SocketHandler.clients:
            client.write_message(json.dumps(message))

    def on_message(self, message):
        message=json.loads(message)
        if message['event']=='message':
            mssg=newMessage(message['message'],message['key'])
            msg={'event':'message', 'message':mssg.text, 'author':{'id':mssg.author.id, 'name':mssg.author.name}, 'timestamp':mssg.timestamp.isoformat()}
            self.send(msg)
        elif message['event']=='alive':
            pass
        elif message['event']=='login':
              user=loginUser(message['name'], message['passwd'])
              msg={'event':'login', 'key':user.key, 'id':user.id, 'errors':[]}
              self.write_message(json.dumps(msg))
              print("User connected!")
              SocketHandler.clients.add(self)
              msg=getMessages()
              self.write_message(json.dumps({'event':'messagedump', 'messages':msg}))
              msg={'event':'connect', 'user':user.name}
              self.send(msg)
        elif message['event']=='register':
               print(message)
               errors=registerUser(message['name'], message['email'], message['passwd'])
               if errors==None: 
                   msg={'event':'register', 'status':'OK'}
                   SocketHandler.clients.add(self)
               else: 
                   msg={'event':'register', 'status':'0', 'error':errors}
               self.write_message(json.dumps(msg))


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
    #http_server.listen(5000)
    tornado.ioloop.IOLoop.instance().start()
