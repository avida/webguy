from flask_raspi import app
from gpio import RaspiGPIOOut
from xbmc import XBMC
from utils import FileBrowser, SystemUptime
import urllib.parse
import html
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

@app.route("/browse")
@app.route("/browse/<string:path>")
def browse(path =  './'):
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

