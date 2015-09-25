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
from utils import FileBrowser
from omxplayer import  OMXPlayer
from twitch import Twitch

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

class BrowserHanlder(FileBrowser):
   def __init__(self, app):
      self.app = app
      FileBrowser.__init__(self,'/root/share')

   def __call__(self, params):
      try:
         path = urllib.parse.unquote('/'.join(params))
         path = html.unescape(path)
         return self.processItemOnFS(path);
      except AttributeError:
         pass
      except FileBrowser.NotADirException:
         path = self.dir_path + '/'+ path
         print (path)
         self.app.player.quitPlayer()
         self.app.player.startPlayer(path)
      return "ok"

class PlayerHandler:
   def __init__(self, app):
      self.app = app

   def __call__(self, params):
      command = params[0]
      if command == "forward":
         self.app.player.forward()
      elif command == "pplay":
         self.app.player.pause()
      elif command == "backward":
         self.app.player.backward()
      elif command == "audio":
         self.app.player.switchAudio()
      return "ok"

class TwitchHandler:
    def __init__(self, app):
        self.app = app
        self.twitch = Twitch()
    def __call__(self, params):
        command = params[0]
        if command == "games":
            try:
                page = int(params[1])
            except Exception:
                page = 0
            return json.dumps(self.twitch.getGames(page))
        elif command == "search":
            game = params[1]
            page = int(params[2])
            print ("game = %s page = %d " % (game, page))
            return json.dumps(self.twitch.searchStreams(game, page))
        elif command == "play":
            channel = params[1]
            self.app.player.quitPlayer()
            self.app.player.startStream("https://www.twitch.tv/"+channel)
        return "Ok"
      
class App:
   def __init__(self):
      self.player = OMXPlayer()
      self.dispatcher = url_handler.UrlDispatcher()
      self.dispatcher.addHandler('/srv/radio', RadioHandler());
      self.dispatcher.addHandler('/srv/socket', SocketHandler());
      self.dispatcher.addHandler('/srv/browse', BrowserHanlder(self));
      self.dispatcher.addHandler('/srv/player', PlayerHandler(self));
      self.dispatcher.addHandler('/srv/twitch', TwitchHandler(self));
   def processRequest(self, req_handler):
      return self.dispatcher.dispatchUrl(req_handler.request.uri)
