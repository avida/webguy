#!/usr/bin/python3
import tornado.ioloop
import tornado.web
import sys
import argparse

cmd_parser = argparse.ArgumentParser()
cmd_parser.add_argument('--app', type=str, default = 'raspi', help="Platform type" )
args = cmd_parser.parse_args()

class Redirect(tornado.web.RequestHandler):

    def get(self):
        index_url = "../page/index.html"
        if args.app and args.app == 'raspi':
            index_url = '../page/raspi/index.html'
        self.render(index_url)

class RaspiMainHandler(tornado.web.RequestHandler):

    def __init__(self, request, handler_kwargs):
        tornado.web.RequestHandler.__init__(self, request, handler_kwargs)

    def getpost(self):
        self.write(RaspiMainHandler.app.processRequest(self))

    def get(self, *args):
        print("get")
        self.getpost()

    def post(self, *args):
        print("post")
        self.getpost()

class MainHandler(tornado.web.RequestHandler):

    def __init__(self, request, handler_kwargs):
        tornado.web.RequestHandler.__init__(self, request, handler_kwargs)

    def get(self, *args):
        print("get")
        self.write(MainHandler.app.processRequest(self))

class GreenhouseHandler(tornado.web.RequestHandler):

    def __init__(self, request, handler_kwargs):
        tornado.web.RequestHandler.__init__(self, request, handler_kwargs)

    def get(self, *args):
        self.write(GreenhouseHandler.app.processRequest(self))

def choseHandler():
    if args.app == 'raspi':
        print("raspi init")
        import raspi
        RaspiMainHandler.app = raspi.App()
        try:
            from serial_listener import startListen
            startListen()
        except Exception as e:
            print("No serial module:", e)
        return RaspiMainHandler
    elif args.app == 'greenhouse':
        import greenhouse
        GreenhouseHandler.app = greenhouse.App()
        return GreenhouseHandler
    else:
        print ("starting default app")
        import app
        MainHandler.app = app.App()
        return MainHandler

handler_class = choseHandler()

application = tornado.web.Application(handlers=[
    (r"/srv/(.*)", handler_class),
    (r"/", Redirect),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": "../page"}),
])

try:
    application.listen(80)
    print('App {} has strated'.format(args.app))
except PermissionError:
    print("Cannot bind to port 80 due to permission error."
          " Please make sure you are eligible of useing network socket")
    exit(1)
tornado.ioloop.IOLoop.instance().start()
# vim: ts=4 sw=4 et
