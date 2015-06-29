#!/usr/bin/python3
import tornado.ioloop
import tornado.web
import sys
app = None
class Dummy:
    def __call__(self, *kwargs):
        pass
class MainHandler(tornado.web.RequestHandler):
    def get(self, *args):
        env = {'REQUEST_URI': self.request.uri, 
                'QUERY_STRING':self.request.query}
        self.write(app(env, Dummy() ))
class Redirect(tornado.web.RequestHandler):
    def get(self):
        self.render('../page/index.html')
if sys.argv[1] == 'raspi':
    import raspi
    print ("raspi init")
    app = raspi.app
else:
    import app
    print ("app init")
    app = app.app
application = tornado.web.Application(handlers=[
        (r"/srv/(.*)", MainHandler),
        (r"/", Redirect),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path":"../page"}),
        ])
application.listen(80)
tornado.ioloop.IOLoop.instance().start()
print('Hello')
# vim: ts=3 sw=3 et
