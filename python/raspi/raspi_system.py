from flask_raspi import app
from flask import abort
from gpio import RaspiGPIOOut
from xbmc import XBMC
from utils import FileBrowser, SystemUptime, ConnectionRefusedHandler
import urllib.parse
import html
import os
import pathlib
xbmc = XBMC()

@app.route("/socket/<int:socket>/<string:action>")
@app.route("/socket/<int:socket>/<string:action>/<int:value>")
def socket(socket, action, value = None):
    p = RaspiGPIOOut(socket)
    if action == 'set':
        p.setValue(value == "1")
        return "ok"
    elif action == 'switch':
        value = p.getValue()
        p.setValue(not value)
        return str(p.getValue())
    elif action == 'get':
        return str(p.getValue())
    return "Unknown command"

@app.route("/music")
@app.route("/music/<string:path>")
@ConnectionRefusedHandler
def musicBrowse(path =  './'):
    browser = FileBrowser('./')
    path = urllib.parse.unquote('/'.join(path))
    path = html.unescape(browser.dir_path + '/' + path)
    type = 'directory'
    if pathlib.Path(path).is_file():
        type = 'file'
    xbmc.Stop()
    xbmc.ClearPlaylist(0)
    xbmc.AddToPlayList(0, path, type=type)
    xbmc.StartPlaylist(0)
    xbmc.SetAudioDevice('PI:Analogue')
    return "ok"
    try:
        path = urllib.parse.unquote('/'.join(params))
        path = html.unescape(path)
        return self.processItemOnFS(path)
    except FileBrowser.NotADirException:
        return "not a dir"

@app.route("/browse/")
@app.route("/browse/<path:path>")
@ConnectionRefusedHandler
def fsBrowse(path = './'):
    browser = FileBrowser('./')
    try:
        path = html.unescape(path)
        return browser.processItemOnFS(path)
    except AttributeError:
        pass
    except FileBrowser.NotADirException:
        path = os.path.normpath(browser.dir_path + '/' + path)
        print(path)
        xbmc.Open(path)
    return "ok"

@app.route('/system/<string:action>')
@ConnectionRefusedHandler
def systemAction(action):

    def GetSystemInfo(self):
        info = {}
        info["uptime"] = str(SystemUptime())
        return info

    if action == 'hdmi':
        xbmc.SetAudioDevice('PI:HDMI')
    elif action == 'analog':
        xbmc.SetAudioDevice('PI:Analogue')
    elif action == 'info':
        return GetSystemInfo()
    else:
        abort(404)

    
