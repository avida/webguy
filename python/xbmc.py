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
      body = self.template % (method, json.dumps(params))
      resp = self.connection.getData(self.url_template % method, headers = self.hdrs, data = body )
      return json.loads(resp)

class XBMC:
   def __init__(self):
      self.rpc = JsonRPC()
      self.activePlayerId = 1

   def GetPlayLists(self):
      return self.rpc.method("Playlist.GetPlaylists", {})

   def GetPlayListItems(self, id):
      return self.rpc.method("Playlist.GetItems", {"playlistid": id})

   def AddToPlayList(self, id, item, type="file"):
      return self.rpc.method("Playlist.Add", {"playlistid":id, "item":{type:item} })

   def ClearPlaylist(self, id):
      return self.rpc.method("Playlist.Clear", {"playlistid":id})

   def StartPlaylist(self, id):
      return self.rpc.method("Player.Open",{"item":{"playlistid":id} } )

   def Open(self, item):
      return self.rpc.method("Player.Open",{"item":{"file":item} } )
      
   def getActivePlayer(self):
      return self.rpc.method("Player.GetActivePlayers", {})

   def DoWithPlayerId(self, func):
      for i in range(0,3):
         resp = func(self)
         print (resp)
         if "error" in resp:
            try:
               print("error: " + json.dumps(resp))
               playerReq = self.getActivePlayer()
               self.activePlayerId = playerReq["result"][0]["playerid"]
            except Exception as e:
               return {"error": e}
         else:
            return resp
      return {}

   def PlayPause(self):
      def _PlayPause(self):
         return self.rpc.method("Player.PlayPause", {"playerid":self.activePlayerId})
      return self.DoWithPlayerId(_PlayPause)

   def Seek(self, val):
      def _Seek(self):
         return self.rpc.method("Player.Seek", {"playerid": self.activePlayerId, "value": val})
      return self.DoWithPlayerId(_Seek)

   def Stop(self):
      def _Stop(self):
         return self.rpc.method("Player.Stop", {"playerid": self.activePlayerId})
      return self.DoWithPlayerId(_Stop)

   def GetPosition(self):
      def _GetPosition(self):
         return self.rpc.method("Player.GetProperties", {"playerid": self.activePlayerId, 
                                                         "properties":["playlistid", "position", "totaltime", "time", "percentage"]})
      return self.DoWithPlayerId(_GetPosition)

   def SetAudioDevice(self, device):
      return self.rpc.method("Settings.SetSettingValue", {'setting': 'audiooutput.audiodevice', 'value': device })

   def openYoutubeVideo(self, video_id): 
      yt_template = "plugin://plugin.video.youtube/?action=play_video&videoid=%s"
      resp = self.rpc.method("Player.Open", {"item": {"file":yt_template % video_id }} )
      return resp

   def openTwitchStream(self, video_id): 
      twitch_template = "plugin://plugin.video.twitch/playLive/%s"
      resp = self.rpc.method("Player.Open", {"item": {"file":twitch_template % video_id }} )
      return resp

if __name__ == "__main__":
   import sys
   rpc = JsonRPC()
   xbmc = XBMC()
   js = None
   if "clear" in sys.argv:
      js = xbmc.ClearPlaylist(0);
   elif "play" in sys.argv:
      js = xbmc.StartPlaylist(0)
   elif "list" in sys.argv:
      js = xbmc.GetPlayListItems(0)
   elif "add" in sys.argv:
      js = xbmc.AddToPlayList(0, "/mnt/music/Music/5nizza", "directory")
   elif "pos" in sys.argv:
      js = xbmc.GetPosition()
   elif "seek" in sys.argv:
      js = xbmc.Seek(54)
   elif "device" in sys.argv:
      js = xbmc.SetAudioDevice('PI:HDMI')
   elif "stop" in sys.argv:
      js = xbmc.Stop()
   print (js)
   print (json.dumps(js, indent=2))
   #js = rpc.method("Files.GetDirectory",{"directory":"/mnt/nfs/.hidden","properties":["size"]} )
   #js = xbmc.openYoutubeVideo('V9WY94PfOs8')
   # js = rpc.method("Player.Open",{"item":{"file":"http://s10.voscast.com:10002"} } )
   #js = xbmc.GetPlayLists()
   #js = xbmc.GetPlayListItems(0)
