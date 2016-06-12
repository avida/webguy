#!/usr/bin/python3
import http.client
import html
import urllib.parse
import os
import sys
import json
import time
import pathlib
from gpio import RaspiGPIOOut
from dirble_backend import Dirble
from mocp import MOCP
import url_handler
from utils import FileBrowser, SystemUptime
from omxplayer import OMXPlayer
import os.path
from twitch import Twitch
from xbmc import XBMC
from youtube import YouTube

mocp = None


def makeErrorResponse(msg):
    return json.dumps({'error': str(msg)})


class RadioHandler:

    def __init__(self, app):
        self.mocp = None
        self.app = app
        self.dirble = None

    def __call__(self, params, **kwargs):
        if not self.dirble:
            self.dirble = Dirble()
        command = params[0]
        if command == "page":
            val = params[1]
            self.dirble.current_page = int(val)
            page_info = self.dirble.loadList()
            print(page_info)
            pi = [{"id": x["id"],
                   "name": x["name"],
                   "country": x["country"],
                   "up": len(x["streams"]) != 0} for x in page_info]
            return json.dumps(pi)
        elif command == "play":
            value = params[1]
            station_info = self.dirble.getStationInfo(int(value))
            if len(station_info["streams"]) > 0:
                stream = station_info["streams"][0]["stream"]
                self.app.xbmc.Open(stream)
                self.app.xbmc.SetAudioDevice('PI:Analogue')
                return stream
        elif command == "stop":
            self.app.xbmc.Stop()
            self.app.xbmc.SetAudioDevice('PI:HDMI')
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

    def __call__(self, params, **kwargs):
        command = params[0]
        socket = params[1]
        p = RaspiGPIOOut(int(socket))
        if command == 'set':
            val = params[2]
            p.setValue(val == "1")
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
        FileBrowser.__init__(self, '/mnt/nfs')

    def __call__(self, params, **kwargs):
        try:
            path = urllib.parse.unquote('/'.join(params))
            path = html.unescape(path)
            return self.processItemOnFS(path)
        except AttributeError:
            pass
        except FileBrowser.NotADirException:
            path = os.path.normpath(self.dir_path + '/' + path)

            print(path)
            self.app.xbmc.Open(path)
        return "ok"


class MusicBrowserHandler(FileBrowser):

    def __init__(self, app):
        self.app = app
        FileBrowser.__init__(self, '/mnt/music')

    def __call__(self, params, **kwargs):
        if len(params) != 0:
            path = urllib.parse.unquote('/'.join(params))
            path = html.unescape(self.dir_path + '/' + path)
            type = 'directory'
            if pathlib.Path(path).is_file():
                type = 'file'
            self.app.xbmc.Stop()
            self.app.xbmc.ClearPlaylist(0)
            self.app.xbmc.AddToPlayList(0, path, type=type)
            self.app.xbmc.StartPlaylist(0)
            self.app.xbmc.SetAudioDevice('PI:Analogue')
            return "ok"
        try:
            path = urllib.parse.unquote('/'.join(params))
            path = html.unescape(path)
            return self.processItemOnFS(path)
        except FileBrowser.NotADirException:
            return "not a dir"


class PlayerHandler:

    def __init__(self, app):
        self.app = app

    def __call__(self, params, **kwargs):
        command = params[0]
        if command == "forward":
            self.app.xbmc.Seek("smallforward")
        elif command == "pplay":
            self.app.xbmc.PlayPause()
        elif command == "backward":
            self.app.xbmc.Seek("smallbackward")
        elif command == "audio":
            self.app.xbmc.Action("audionextlanguage")
        elif command == "info":
            return self.playerInfo()
        elif command == "seek":
            val = int(params[1])
            return json.dumps(self.app.xbmc.Seek(val)["result"])
        elif command == "volume":
            operation = params[1]
            if operation == "get":
                vol = self.app.xbmc.getVolume()["result"]["volume"]
                return str(vol)
            elif operation == "set":
                val = int(params[2])
                self.app.xbmc.setVolume(val)
                return "ok"
            return "invalid request"
        return "ok"

    def playerInfo(self):
        try:
            position = self.app.xbmc.GetPosition()["result"]
            position["label"] = self.app.xbmc.GetItem()["result"][
                "item"]["label"]
            return json.dumps(position)
        except Exception as e:
            return makeErrorResponse(e)


class TwitchHandler:

    def __init__(self, app):
        self.app = app
        self.twitch = Twitch()

    def __call__(self, params, **kwargs):
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
            print("game = %s page = %d " % (game, page))
            return json.dumps(self.twitch.searchStreams(game, page))
        elif command == "play":
            channel = params[1]
            print(str(params))
            self.app.xbmc.openTwitchStream(channel)
        return "Ok"


class YouTubeHandler:

    def __init__(self, app):
        self.app = app
        self.yt = YouTube()

    def __call__(self, params, **kwargs):
        command = params[0]
        print(kwargs["handler"].request.body)
        if command == "search":
            val = urllib.parse.unquote(params[1])
            try:
                js = self.yt.search(val)
            except Exception:
                return "not ok"
            items = [[x["id"]["videoId"],
                      x["snippet"]["title"],
                      x["snippet"]["thumbnails"]["medium"]["url"],
                      x["snippet"]["publishedAt"]] for x in js["items"] if x["id"]["kind"] == "youtube#video"]
            res = {"items": items}
            if "nextPageToken" in js:
                res["nextToken"] = js["nextPageToken"]
            if "prevPageToken" in js:
                res["prevToken"] = js["prevPageToken"]
            result = json.dumps(res, indent=1)
            return result
        elif command == "play":
            try:
                self.app.xbmc.openYoutubeVideo(params[1])
                return "ok"
            except IndexError:
                return "not ok"
        return "Not found"


class SystemHandler:

    def __init__(self, app):
        self.app = app

    def __call__(self, params, **kwargs):
        command = params[0]
        if command == 'hdmi':
            self.app.xbmc.SetAudioDevice('PI:HDMI')
        elif command == 'analog':
            self.app.xbmc.SetAudioDevice('PI:Analogue')
        elif command == 'info':
            return self.GetSystemInfo()
        return 'ok'

    def GetSystemInfo(self):
        info = {}
        info["uptime"] = str(SystemUptime())
        return info


class App:

    def __init__(self):
        self.xbmc = XBMC()
        self.dispatcher = url_handler.UrlDispatcher()
        self.dispatcher.addHandler('/srv/radio', RadioHandler(self))
        self.dispatcher.addHandler('/srv/socket', SocketHandler())
        self.dispatcher.addHandler('/srv/browse', BrowserHanlder(self))
        self.dispatcher.addHandler('/srv/player', PlayerHandler(self))
        self.dispatcher.addHandler('/srv/twitch', TwitchHandler(self))
        self.dispatcher.addHandler('/srv/youtube', YouTubeHandler(self))
        self.dispatcher.addHandler('/srv/music', MusicBrowserHandler(self))
        self.dispatcher.addHandler('/srv/system', SystemHandler(self))

    def processRequest(self, req_handler):
        return self.dispatcher.dispatchUrl(req_handler.request.uri, req_handler=req_handler)
