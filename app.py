import tornado.httpserver
import tornado.ioloop
import tornado.websocket
import tornado.web
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
    def open(self):
        #name=tornado.websocket.WebSocketHandler.get_body_argument(self,'a')
        #self.write_message(u"Name: "+name)
        #print(name)
        SocketHandler.clients.add(self)
        print("User connected!")
        self.send("User connected!")

    def check_origin(self, origin):
        return True

    def send(self, message):
        for client in SocketHandler.clients:
            client.write_message(message)

    def on_message(self, message):
        #print("Message: "+message) DEBUG
        self.send(message)


    def on_close(self):
        SocketHandler.clients.remove(self)
        print("Connection closed")

application = tornado.web.Application([
    (r"/", SocketHandler),
    (r"/chat", MainHandle),
], **settings)

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(os.environ.get('PORT', 5000))
    tornado.ioloop.IOLoop.instance().start()
