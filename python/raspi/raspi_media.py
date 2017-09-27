from flask_raspi import app
from flask import abort
from xbmc import XBMC
from dirble_backend import Dirble
from mocp import MOCP
from utils import ConnectionRefusedHandler, makeErrorResponse
import json

dirble = Dirble()
xbmc = XBMC()
mocp = MOCP()

@app.route("/radio/page/<int:number>")
@ConnectionRefusedHandler
def browseRadio(number):
    dirble.current_page = number
    page_info = dirble.loadList()
    pi = [{"id": x["id"],
           "name": x["name"],
           "country": x["country"],
           "up": len(x["streams"]) != 0} for x in page_info]
    return json.dumps(pi)

@app.route("/radio/play/<int:station>")
@ConnectionRefusedHandler
def playStation(station):
    station_info = self.dirble.getStationInfo(station )
    if len(station_info["streams"]) > 0:
        stream = station_info["streams"][0]["stream"]
        xbmc.Open(stream)
        xbmc.SetAudioDevice('PI:Analogue')
        return stream

@app.route("/radio/stop")
@ConnectionRefusedHandler
def radioStop():
    xbmc.Stop()
    xbmc.SetAudioDevice('PI:HDMI')
    return "stopped"

@app.route("/radio/info")
def getInfo():
    return MOCP.getCurrentTitle()

@app.route("/volume/<string:action>")
def radioVolume(action):
    if action == "up":
        mocp.volumeUp()
    elif action == "down":
        mocp.volumeDown()
    elif action == 'get':
        return str(MOCP.volume())
    else:
        abort(404)
    return str(mocp.vol)

@app.route("/volume/set/<int:value>")
def radioSetVolume(value):
    MOCP.setVolume(value)
    return 'ok'

def playerInfo():
    position = xbmc.GetPosition()["result"]
    position["label"] = xbmc.GetItem()["result"][
        "item"]["label"]
    return json.dumps(position)

@app.route("/player/<string:action>")
@app.route("/player/<string:action>/<int:value>")
@ConnectionRefusedHandler
def playerAction(action, value = None):
    if action == "forward":
        xbmc.Seek("smallforward")
    elif action == "pplay":
        xbmc.PlayPause()
    elif action == "backward":
        xbmc.Seek("smallbackward")
    elif action == "audio":
        xbmc.Action("audionextlanguage")
    elif action == "info":
        return playerInfo()
    elif action == "seek":
        return json.dumps(xbmc.Seek(value)["result"])
    elif action == "playlist":
        js = xbmc.GetPlayListItems(0)
        return json.dumps(js["result"])
    elif action == "goto":
        js = xbmc.Goto(value)
        return json.dumps(js)
    else:
        abort(404)

@app.route("/player/volume/<string:action>")
@app.route("/player/volume/<string:action>/<int:value>")
@ConnectionRefusedHandler
def changeVolume(action, value = None):
    print ("action is {}, value is {}".format(action,value))
    if action == "get":
        vol = xbmc.getVolume()["result"]["volume"]
        return str(vol)
    elif action == "set":
        xbmc.setVolume(value)
        return "ok"
    else:
        abort(404)
    
