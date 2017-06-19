import url_handler
from gpio import RaspiGPIOOut

class LampHandler:

    def __init__(self):
        self.gpio = RaspiGPIOOut(3)

    def __call__(self, params, **kwargs):
        try:
            command = params[0]
        except:
            return "wrong request"
        if command == 'on':
            self.gpio.setValue(True)
        elif command == 'off':
            self.gpio.setValue(False)
        elif command != 'state':
            return "wrong request"
        return "{}".format(self.gpio.getValue())
        
class App:

    def __init__(self):
       self.dispatcher = url_handler.UrlDispatcher()
       self.dispatcher.addHandler('/srv/lamp', LampHandler())

    def processRequest(self, req_handler):
        return self.dispatcher.dispatchUrl(req_handler.request.uri)
