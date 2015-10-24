#!/usr/bin/python3
import tornado.ioloop
import tornado.web
import sys

class Redirect(tornado.web.RequestHandler):
    def get(self):
        index_url = "../page/index.html"
        if len(sys.argv) > 1 and sys.argv[1] == 'raspi':
            index_url = '../page/raspi/index.html'
        self.render(index_url)
web_app = None
class RaspiMainHandler(tornado.web.RequestHandler):
    def __init__(self, request, handler_kwargs):
        tornado.web.RequestHandler.__init__(self, request, handler_kwargs)
        global web_app
        if not web_app:
            import raspi
            web_app = raspi.App()
    def get(self, *args):
        print ("get")
        global web_app
        self.write(web_app.processRequest(self))

class MainHandler(tornado.web.RequestHandler):
    def __init__(self, request, handler_kwargs):
        tornado.web.RequestHandler.__init__(self, request, handler_kwargs)
        global web_app
        if not web_app:
            import app
            web_app = app.App()
    def get(self, *args):
        print ("get")
        global web_app
        self.write(web_app.processRequest(self))

handler_class = MainHandler
if 'raspi' in sys.argv:
    print ("raspi init")
    try:
        from  serial_listener import startListen
        startListen()
    except Exception as e:
        print ("No serial module:", e)
    handler_class = RaspiMainHandler
else:
    print ("main hanlder")

application = tornado.web.Application(handlers=[
        (r"/srv/(.*)", handler_class),
        (r"/", Redirect),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path":"../page"}),
        ])
application.listen(80)
tornado.ioloop.IOLoop.instance().start()
print('Hello')
# vim: ts=3 sw=3 et
