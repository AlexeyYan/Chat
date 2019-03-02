import os
import json
from datetime import datetime
from hashlib import md5
import tornado.httpserver
import tornado.ioloop
import tornado.websocket
import tornado.web
from db_handler import db, loginUser, registerUser, newMessage, getMessages, newFile
from db_models import *


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    "static_url_prefix": "/static/",
}


class MainHandler(tornado.web.RequestHandler):
    def get(self):#Return main page
        MainHandler.render(self, "templates/main.html")

class PersonHandler(tornado.web.RequestHandler):
    def get(self):
        user_id=self.get_argument('id',None)
        if user_id:
            user=db.query(User).filter_by(id=user_id)
            if user:
                PersonHandler.render(self,"templates/person.html", user=user)



class FileHandler(tornado.web.RequestHandler):
    '''
   methods: post
   Description: This class is designed to receive and process ajax-request for 
                file uploading
'''
    def post(self):
        attch_list=[]
        for client in SocketHandler.clients:
            if client.key == self.get_argument('key'):
                owner = client
        if (owner):
            for file in self.request.files['files[]']:
                attch_list.append(newFile(file, self.get_argument('key')))
            owner.write_message(json.dumps({'event':'attach_response', 'files':attch_list}))

 
class SocketHandler(tornado.websocket.WebSocketHandler):
    '''
   methods: open, check_origin, on_message, on_close, send
   Description: This class is the main class of the application. 
                It processes messages coming via the WebSocket protocol.
'''
    clients = set()#Set of connected clients
    key = ''#Key of client
    user=None
    def open(self):
        print("Client connected!")
        

    def check_origin(self, origin):
        return True

    def send(self, message):#Send message for all connected clients
        for client in SocketHandler.clients:
            client.write_message(json.dumps(message))

    def on_message(self, message):
        message = json.loads(message)
        if message['event'] == 'message':
            if self not in SocketHandler.clients:
                return
            msg = newMessage(message)
            self.send(msg)

        elif message['event'] == 'alive':#Event to maintain connection
            pass

        elif message['event'] == 'login':
            self.user = loginUser(message['name'], message['passwd'])
            print(self.user)
            if self.user:
                msg = {'event': 'login', 'status':'true', 'key': self.user.key,
                       'id': self.user.id}
                self.write_message(json.dumps(msg))
                print("User connected!")
                SocketHandler.clients.add(self)
                self.key = self.user.key
                messg = getMessages()
                self.write_message(json.dumps(
                    {'event': 'messagedump', 'messages': messg}))
                msg = {'event': 'connect', 'user': self.user.name}
                self.send(msg)
                self.dis={'event': 'disconnect', 'user': self.user.name}
            else:
                msg={'event': 'login', 'status':'false'}
                self.write_message(json.dumps(msg))
                print('false')


        elif message['event'] == 'register':
            print(message)
            errors = registerUser(
                message['name'], message['email'], message['passwd'])
            if not errors:
                msg = {'event': 'register', 'status': 'true'}
                SocketHandler.clients.add(self)
            else:
                msg = {'event': 'register', 'status': 'false', 'error': errors}
            self.write_message(json.dumps(msg))

    def on_close(self):
        SocketHandler.clients.remove(self)
        print("Connection closed")


application = tornado.web.Application([
    (r"/", SocketHandler),
    (r"/chat", MainHandler),
    (r"/upload", FileHandler),
    (r"/images/(.*)", tornado.web.StaticFileHandler, {"path": "./images"}),
    ("r/person(.*)", PersonHandler),
], **settings)


if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(os.environ.get('PORT', 5000))
    tornado.ioloop.IOLoop.instance().start()
