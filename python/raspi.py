#!/usr/bin/python3
import http.client
#from flipflop import WSGIServer
import html
from utils import runCommand
from mpc import spawnPlayer, MPCPlayer
import urllib.parse
import os
import sys
import json
import threading
import time
from wol import WOLThread
from dlna import getDLNAItems
from gpio import RaspiGPIOOut
from dirble_backend import Dirble
from mocp import MOCP

logfile=open("./log.txt",'w')
mpc = MPCPlayer()
dirble = None
mocp = None

def Log(msg):
  logfile.write(msg+'\n')
  logfile.flush()

def printError(e, start_resp):
   start_resp('200 OK', [('Content-Type', 'text/plain')])
   return str(e)
   
def getDirsAndFiles(path):
   _, d, f = next(os.walk(path))
   return d, f

def getElementWithId(elements, id_name, id_value):
   for el in elements:
      if el.getAttribute(id_name) == id_value:
         return el

def sendVLCRequest(params=None):
   c = http.client.HTTPConnection("127.0.0.1:8080")
   url = "/requests/status.xml"
   if params:
      url += "?" + params
   c.request("GET", url, headers={"Authorization": "Basic OjE4ODg="})
   resp = c.getresponse()
   data = resp.read().decode('utf-8')
   return data
      
def getVLCInfo(data=None):
   from xml.dom.minidom import parseString
   if not data:
      data = sendVLCRequest()
   dom = parseString(data)
   filename = getVLCInfoFilename(dom)
   volume = getVLCBaseInfo(dom, "volume");
   length = getVLCBaseInfo(dom, "length");
   position = getVLCBaseInfo(dom, "position");
   return json.dumps({"filename": filename, "volume": volume,\
                     "length": length, "position":position } )

def processItemOnFS(start_resp, path):
   base_path=r'\\192.168.1.115\share'
   full_path = "%s\%s" % (base_path, path)
   Log("request "+ full_path)
   wolthread = WOLThread()
   wolthread.start()
   try:
      if os.path.isfile(full_path):
         Log("is file")
         spawnPlayer(full_path)
         start_resp('200 OK', [('Content-Type', 'text/plain')])
         return "" 
      else:
         dirs, files = getDirsAndFiles(full_path);
         dirs.sort()
         files.sort()
         data = json.dumps({"dirs": dirs, "files": files})
         start_resp('200 OK', [('Content-Type', 'text/plain')])
         return data
   finally:
      pass
      wolthread.Stop()

def processDLNAData(start_resp, path):
   if not path:
      dirs, files = getDLNAItems()
   else:
      dirs, files = getDLNAItems(path)
   data = json.dumps({"dirs": dirs, "files": files})
   start_resp('200 OK', [('Content-Type', 'text/plain')])
   return data

def app(env, start_resp):
   url = env.get('REQUEST_URI')
   url = url.split('/')[2:] # split result: '' , 'srv', 'request itself'
   try:
      if "suspend" in url:
         try:
            data = runCommand('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
            start_resp('200 OK', [('Content-Type', 'text/plain')])
            return str(data)
         except Exception as e:
            printError(e, start_resp)
      elif "forward" in url:
         #data = sendVLCRequest("command=seek&val=+30S")
         #data = getVLCInfo(data)
         #start_resp('200 OK', [('Content-Type', 'text/plain')])
         mpc.jumpFForward()
         return ''
      elif "socket" in url:
         s = url[2]
         p = RaspiGPIOOut(int(s))
         if "switch" in url:
            val = p.getValue()
            p.setValue(not val)
            return "ok"
         if not "get" in url:
            val = url[3]
            p.setValue(val == "1")
         return str(p.getValue())
      elif "radio" in url:
         command = url[1]
         global dirble
         if not dirble:
            dirble = Dirble()
         if command == "page":
             value = url[2]
             dirble.current_page = int(value)
             page_info = dirble.loadList()
             pi = [ {"id":x["id"], 
                     "name": x["name"], 
                     "country": x["country"],
                     "up": len(x["streams"]) != 0 } for x in page_info]
             return json.dumps(pi)
         elif command == "play":
             value = url[2]
             station_info = dirble.getStationInfo(int(value))
             if len(station_info["streams"]) > 0:
                stream = station_info["streams"][0]["stream"]
                MOCP.play(stream)
                return stream
             return "no stream"
         elif command == "stop":
             MOCP.stop()
             return "stopped"
         elif command == "info":
             return MOCP.getCurrentTitle()
         elif command == "volume":
             val = url[2]
             global mocp
             if not mocp:
                mocp = MOCP()
             if val == "up":
                mocp.volumeUp()
             elif val == "down":
                mocp.volumeDown()
             elif val == 'set':
                newval = url[3]
                MOCP.setVolume(int(newval))
                return 'ok'
             elif val == 'get':
                return str(MOCP.volume())
             return str(mocp.vol)
         return "Unknown command"
      return "Sorry cannot server this"
            
   except Exception as e:
      return printError(e, start_resp)
#WSGIServer(app).run()
