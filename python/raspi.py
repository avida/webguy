#!/usr/bin/python3
import http.client
import html
import urllib.parse
import os
import sys
import json
import time
from gpio import RaspiGPIOOut
from dirble_backend import Dirble
from mocp import MOCP
import url_handler

mocp = None
class RadioHandler:
    def __init__(self):
        self.mocp = None
        self.dirble = None

    def __call__(self, params):
        if not self.dirble:
            self.dirble = Dirble()
        command = params[0]
        if command == "page":
            val = params[1]
            self.dirble.current_page = int(val)
            page_info = self.dirble.loadList()
            pi = [ {"id":x["id"], 
                    "name": x["name"], 
                    "country": x["country"],
                    "up": len(x["streams"]) != 0 } for x in page_info]
            return json.dumps(pi)
        elif command == "play":
            value = params[1]
            station_info = self.dirble.getStationInfo(int(value))
            if len(station_info["streams"]) > 0:
               stream = station_info["streams"][0]["stream"]
               MOCP.play(stream)
               return stream
        elif command == "stop":
            MOCP.stop()
            return "stopped"
        elif command == "info":
            return MOCP.getCurrentTitle()
        elif command == "volume":
            val = params[1]
            if not self.mocp:
               self.mocp = MOCP()
            if val == "up":
               self.mocp.volumeUp()
            elif val == "down":
               self.mocp.volumeDown()
            elif val == 'set':
               newval = params[2]
               MOCP.setVolume(int(newval))
               return 'ok'
            elif val == 'get':
               return str(MOCP.volume())
            return str(self.mocp.vol)

class SocketHandler:
    def __call__(self, params):
        command = params[0]
        socket = params[1]
        p = RaspiGPIOOut(int(socket))
        if command == 'set':
            val = params[2]
            p.setValue(val == "1");
            return "ok"
        elif command == 'switch':
            val = p.getValue()
            p.setValue(not val)
            return str(p.getValue())
        elif command == 'get':
           return str(p.getValue())
        return "Unknown command"
      
class App:
   def __init__(self):
      self.dispatcher = url_handler.UrlDispatcher()
      self.dispatcher.addHandler('/srv/radio', RadioHandler());
      self.dispatcher.addHandler('/srv/socket', SocketHandler());

   def processRequest(self, req_handler):
      return self.dispatcher.dispatchUrl(req_handler.request.uri)
