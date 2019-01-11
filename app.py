from hashlib import md5
import tornado.httpserver
import tornado.ioloop
import tornado.websocket
import tornado.web
from db_handler import db, loginUser, registerUser, newMessage, getMessages, newFile
from datetime import datetime
import json
import time
import os


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    "static_url_prefix": "/static/",
}


class MainHandler(tornado.web.RequestHandler):
    def get(self):#Return main page
        MainHandler.render(self, "templates/main.html")


'''Class FileHandler(tornado.web.RequestHandler):
   methods: post
   Description: This class is designed to receive and process ajax-request for 
                file uploading
''' 
class FileHandler(tornado.web.RequestHandler):
    def post(self):
        for client in SocketHandler.clients:
            if client.key == self.get_argument('key'):
                print("Find")
                owner = client
                for file in self.request.files['files[]']:
                    owner.attch_list.append(
                        newFile(file, self.get_argument('key')))
        #print("Get file")

'''class SocketHandler(tornado.websocket.WebSocketHandler):
   methods: open, check_origin, on_message, on_close, send
   Description: This class is the main class of the application. 
                It processes messages coming via the WebSocket protocol.
'''
 
class SocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()#Set of connected clients
    key = ''#Key of client
    attch_list = []#list of attachments that client upload for message

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
            msg = newMessage(message, self.attch_list)
            self.send(msg)
            self.attch_list.clear()

        elif message['event'] == 'alive':#Event to maintain connection
            pass

        elif message['event'] == 'login':
            user = loginUser(message['name'], message['passwd'])
            msg = {'event': 'login', 'key': user.key,
                   'id': user.id, 'errors': []}
            self.write_message(json.dumps(msg))
            print("User connected!")
            SocketHandler.clients.add(self)
            self.key = user.key
            messg = getMessages()
            self.write_message(json.dumps(
                {'event': 'messagedump', 'messages': messg}))
            msg = {'event': 'connect', 'user': user.name}
            self.send(msg)

        '''elif message['event'] == 'register':
            print(message)
            errors = registerUser(
                message['name'], message['email'], message['passwd'])
            if errors == None:
                msg = {'event': 'register', 'status': 'OK'}
                SocketHandler.clients.add(self)
            else:
                msg = {'event': 'register', 'status': '0', 'error': errors}
            self.write_message(json.dumps(msg))'''

    def on_close(self):
        SocketHandler.clients.remove(self)
        print("Connection closed")


application = tornado.web.Application([
    (r"/", SocketHandler),
    (r"/chat", MainHandler),
    (r"/upload", FileHandler),
    (r"/images/(.*)", tornado.web.StaticFileHandler, {"path": "./images"},)
], **settings)


if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(os.environ.get('PORT', 5000))
    tornado.ioloop.IOLoop.instance().start()
