from flask_raspi import app
from flask import abort
from xbmc import XBMC
from dirble_backend import Dirble
from mocp import MOCP
dirble = Dirble()
xbmc = XBMC()
mocp = MOCP()

@app.route("/radio/page/<int:number>")
def browseRadio(number):
    dirble.current_page = number
    page_info = dirble.loadList()
    pi = [{"id": x["id"],
           "name": x["name"],
           "country": x["country"],
           "up": len(x["streams"]) != 0} for x in page_info]
    return json.dumps(pi)

@app.route("/radio/play/<int:station>")
def playStation(station):
    station_info = self.dirble.getStationInfo(station )
    if len(station_info["streams"]) > 0:
        stream = station_info["streams"][0]["stream"]
        xbmc.Open(stream)
        xbmc.SetAudioDevice('PI:Analogue')
        return stream

@app.route("/radio/stop")
def radioStop():
    app.xbmc.Stop()
    app.xbmc.SetAudioDevice('PI:HDMI')
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

