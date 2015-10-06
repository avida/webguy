#!/usr/bin/python3
import json
from web_backend import ServiceConnection

class JsonRPC:
   def __init__(self):
      self.connection = ServiceConnection("127.0.0.1:8080")
      self.template = '{"jsonrpc":"2.0","id":"1","method":"%s","params":%s}'
      self.url_template = "/jsonrpc?%s"
      self.hdrs = {"Content-Type": "application/json"}

   def method(self, method, params):
      print (self.template)
      body = self.template % (method, json.dumps(params))
      resp = self.connection.getData(self.url_template % method, headers = self.hdrs, data = body )
      return json.loads(resp)

class XBMC:
   def __init__(self):
      self.rpc = JsonRPC()
   def BrowserDir(self, dir):
      pass
   def AddToPlayList(self,item):
      pass
   def Open(self, item):
      return self.rpc.method("Player.Open",{"item":{"file":item} } )
      
   def getActivePlayer():
      return self.rpc.method("Player.GetActivePlayers", {})

   def openYoutubeVideo(self, video_id): 
      yt_template = "plugin://plugin.video.youtube/?action=play_video&videoid=%s"
      resp = self.rpc.method("Player.Open", {"item": {"file":yt_template % video_id }} )
      return resp

   def openTwitchStream(self, video_id): 
      twitch_template = "plugin://plugin.video.twitch/playLive/%s"
      resp = self.rpc.method("Player.Open", {"item": {"file":twitch_template % video_id }} )
      return resp

if __name__ == "__main__":
   rpc = JsonRPC()
   xbmc = XBMC()
   js = rpc.method("Files.GetDirectory",{"directory":"/mnt/nfs/.hidden","properties":["size"]} )
   #js = xbmc.openYoutubeVideo('V9WY94PfOs8')
   # js = rpc.method("Player.Open",{"item":{"file":"http://s10.voscast.com:10002"} } )
   print (json.dumps(js, indent=2))
