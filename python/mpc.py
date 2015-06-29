#!/usr/bin/python
import http.client
import threading
import re
from utils import runCommand

player_thread = None

def runPlayer(path):
   #runCommand("export DISPLAY=:0;sudo -u dima vlc -f \"%s\" &" % path)
   #runCommand("sudo -u dima totem --fullscreen --display=:0 \"%s\"" % path)
   #runCommand("export DISPLAY=:0; sudo -u dima mplayer --fs \"%s\"" % path)
   #runCommand(r'"c:\Program Files (x86)\vlc-2.2.0\vlc.exe" -f "%s"' % path) 
   runCommand(r'"c:\Program Files (x86)\K-Lite Codec Pack\MPC-HC64\mpc-hc64.exe" /fullscreen "%s"' % path)

def spawnPlayer(path):
   global player_thread
   #if player_thread:
   #   runCommand("sudo -u dima pkill -9 mplayer")
   player_thread = threading.Thread(target=runPlayer, args=(path, ))
   player_thread.start()
 
mpc_ep = '127.0.0.1:13579'
command_url = "/command.html"
var_url = "/variables.html"
reg_exp = r'<p id="%s">(.*)</p>'
state_reg = re.compile(reg_exp % 'state')
PAUSE_STATE = '1'
PLAY_STATE = '2'
position_reg = re.compile(reg_exp % 'positionstring')
duration_reg = re.compile(reg_exp % 'durationstring')
size_reg = re.compile(reg_exp % 'size')
file_reg = re.compile(reg_exp % 'file')
def safeGetValue(data, exp):
   try:
      return re.search(exp, data).group(1)
   except:
      return ''
def parseMPCInfo(data):
   return {
      'duration': safeGetValue(data, duration_reg),
      'position': safeGetValue(data, position_reg),
      'file'    : safeGetValue(data, file_reg),
      'state'   : safeGetValue(data, state_reg)
      }
class MPCPlayer:
   def createConn(self):
      self.c = http.client.HTTPConnection(mpc_ep)
   def __init__(self):
      self.createConn()
   def sendCommandRequest(self, body):
      try:
         self.c.request("POST", command_url, body)
         resp = self.c.getresponse()
         return resp.read()
      except:
         self.createConn()
         return "Error, connecting again"
   def sendCommandCode(self, code):
      self.sendCommandRequest('wm_command=%d' % code)
   def getInfo(self):
      self.c.request("GET", var_url)
      resp = self.c.getresponse()
      data = resp.read().decode('utf-8')
      match = re.search(state_reg, data)
      return parseMPCInfo(data)
   def pplay(self):
      self.sendCommandCode(889)
   def play(self):
      self.sendCommandCode(887)
   def pause(self):
      self.sendCommandCode(888)
   def nextAudio(self):
      self.sendCommandCode(952)
   def seek(self, percent):
      self.sendCommandRequest('wm_command=-1&percent=%d' % percent)
   def jumpForward(self):
      self.sendCommandCode(900)
   def jumpFForward(self):
      self.sendCommandCode(902)   
   def jumpFFForward(self):
      self.sendCommandCode(904)
   def jumpBack(self):
      self.sendCommandCode(899)
   def jumpBBack(self):
      self.sendCommandCode(901)
   def jumpBBBack(self):
      self.sendCommandCode(903)
   def fullscreen(self):
      self.sendCommandCode(830)
if __name__ == "__main__":
   player = MPCPlayer()
   print(player.getInfo())
   player.fullscreen()
   #player.seek(2)