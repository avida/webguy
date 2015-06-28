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

logfile=open("./log.txt",'w')
mpc = MPCPlayer()
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

def getVLCInfoFilename(dom):
   information = dom.documentElement.getElementsByTagName("information")[0]
   category = getElementWithId(information.getElementsByTagName("category"), "name", "meta")
   info = getElementWithId(category.getElementsByTagName("info"), "name", "filename")
   return info.childNodes[0].nodeValue

def getVLCBaseInfo(dom, tag):
   return dom.documentElement.getElementsByTagName(tag)[0].\
          childNodes[0].nodeValue

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
   url = url.split('/')[2:]
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
      elif "backward" in url:
         #data = getVLCInfo(sendVLCRequest("command=seek&val=-30S"))
         #start_resp('200 OK', [('Content-Type', 'text/plain')])
         mpc.jumpBBack()
         return ''
      elif "pplay" in url:
         #data = getVLCInfo(sendVLCRequest('command=pl_pause'))
         mpc.pplay()
         return ''
      elif "audio" in url:
         mpc.nextAudio()
         return ""
      elif "playerinfo" in url:
         try:
            data = json.dumps(mpc.getInfo())
            start_resp('200 OK', [('Content-Type', 'text/plain')])
            return data
         except Exception as e:
            return printError(e, start_resp)
      elif url[0] == "browse":
         try:
            path = urllib.parse.unquote("/".join(url[1:]))
            path = html.unescape(path)
            return processItemOnFS(start_resp,path)
         except Exception as e:
            return printError(e, start_resp)
      elif url[0] == "play":
         qs = env.get('QUERY_STRING')
         query = urllib.parse.parse_qs(qs)
         url=query['url'][0]
         spawnPlayer(url)
         start_resp('200 OK', [('Content-Type', 'text/plain')])
         return ""
      elif url[0] == 'key':
         key = url[1]
         out = runCommand("export XAUTHORITY=/home/dima/.Xauthority; export DISPLAY=:0; sudo xdotool key "+key)
         start_resp('200 OK', [('Content-Type', 'text/plain')])
         return out
      return ""
   except Exception as e:
      return printError(e, start_resp)

def printenvironent(env, start_resp):
   start_resp('200 OK', [('Content-Type', 'text/html')])
   yield '<h1>Environment<h1>'
   try:
      length = int (env.get('CONTENT_LENGTH', '0'))
      if length:
         data = env['wsgi.input'].read(length)
         yield data.decode('ascii')
   except Exception as e:
      yield str(e)
   yield '<table>'
   for k, v in sorted(env.items()):
      yield '<tr><th>%s</th><td>%s</td></tr>' % (k , v)
   yield '</table>'

#WSGIServer(app).run()
