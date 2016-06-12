#!/usr/bin/python3
import http.client
#from flipflop import WSGIServer
import html
from utils import runCommand, FileBrowser
from mpc import spawnPlayer, MPCPlayer
import urllib.parse
import os
import sys
import json
import threading
import time
from wol import WOLThread
from dlna import getDLNAItems
import url_handler

logfile = open("./log.txt", 'w')


def Log(msg):
    logfile.write(msg + '\n')
    logfile.flush()


class TestHandler:

    def __call__(self, params):
        return "testddd " + str(params)


class BrowserHanlder(FileBrowser):

    def __init__(self):
        FileBrowser.__init__(self, '\\192.168.1.115\share', True)

    def __call__(self, params):
        try:
            path = urllib.parse.unquote('/'.join(params))
            path = html.unescape(path)
            return self.processItemOnFS(path)
        except AttributeError:
            pass
        except FileBrowser.NotADirException:
            spawnPlayer('/'.join(params))
            return "ok"


class MPCRequestHandler:

    def __init__(self):
        self.mpc = MPCPlayer()

    def __call__(self, params):
        if "forward" in params:
            self.mpc.jumpFForward()
        elif "play" in params:
            qs = env.get('QUERY_STRING')
            query = urllib.parse.parse_qs(qs)
            url = query['url'][0]
            spawnPlayer(url)
            start_resp('200 OK', [('Content-Type', 'text/plain')])
            return ""
        elif "backward" in params:
            self.mpc.jumpBBack()
        elif "pplay" in params:
            self.mpc.pplay()
        elif "audio" in params:
            self.mpc.nextAudio()
        elif "fullscreen" in params:
            self.mpc.fullscreen()
        elif "playerinfo" in params:
            try:
                data = json.dumps(self.mpc.getInfo())
                start_resp('200 OK', [('Content-Type', 'text/plain')])
                return data
            except Exception as e:
                return str(e)
        return "Ok"


class SystemRequestHandler:

    def __call__(self, params):
        if "suspend" in params:
            try:
                data = runCommand(
                    'rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
                start_resp('200 OK', [('Content-Type', 'text/plain')])
                return str(data)
            except Exception as e:
                return str(e)
        elif "key" in params:
            key = params[1]
            out = runCommand(
                "export XAUTHORITY=/home/dima/.Xauthority; export DISPLAY=:0; sudo xdotool key " + key)
            return out
        return "Unknown request"


class App:

    def __init__(self):
        self.dispatcher = url_handler.UrlDispatcher()
        self.dispatcher.addHandler('/srv/test', TestHandler())
        self.dispatcher.addHandler('/srv/browse', BrowserHanlder())
        self.dispatcher.addHandler('/srv/player', MPCRequestHandler())
        self.dispatcher.addHandler('/srv/system', SystemRequestHandler())

    def processRequest(self, req_handler):
        return self.dispatcher.dispatchUrl(req_handler.request.uri)
