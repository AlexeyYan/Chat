import tornado.httpserver
import tornado.ioloop
import tornado.websocket
import tornado.web
import time

#class MainHandler(tornado.web.RequestHandler):
 #   def get(self):
  #      self.write(tornado.web.RequestHandler.get_argument(self,'a',40))

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

    def on_message(self, message):
        print("Message: "+message)
        self.write_message(message)

    def send(self, message):
        for client in self.clients:
            client.write_message(message)

    def on_close(self):
        print("Connection closed")

application = tornado.web.Application([
    (r"/", SocketHandler),
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(os.environ.get('PORT', 5000))
    tornado.ioloop.IOLoop.instance().start()
