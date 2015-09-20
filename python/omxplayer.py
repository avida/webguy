#!/usr/bin/python3
import subprocess
import time

def runCommand(cmd):
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
  return p.communicate()

class OMXPlayer:
    def __init__(self):
        self.proc = None

    def startPlayer(self, params):
        cmd = "omxplayer \"%s\"" % params
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

    def quitPlayer(self):
        self.sendKey(b'q')
        time.sleep(5)

    def pause(self):
        self.sendKey(b'p')

    def forward(self):
        # Look for ANSI escape codes here: https://en.wikipedia.org/wiki/ANSI_escape_code
        self.sendKey(b'\x1C[C')
    def backward(self):
        # Look for ANSI escape codes here: https://en.wikipedia.org/wiki/ANSI_escape_code
        self.sendKey(b'\x1D[D')
    def switchAudio(self):
        self.sendKey(b'k')

    def sendKey(self, key):
        try:
            if self.proc:
                self.proc.stdin.write(key)
                self.proc.stdin.flush()
        except BrokenPipeError:
            self.proc = None
        

if __name__ == "__main__":
    print("Run omxplayer module util")
    try:
        player = OMXPlayer()     
        player.startPlayer('/root/Fargo.DVDRip_0dayTeam.avi')
        time.sleep(10)
        print ("step forward")
        player.quitPlayer()
        time.sleep(5)
        print ("step forward")
        player.forward()
        while True:
            time.sleep(29)
        
    except KeyboardInterrupt:
        print ("exiting player")
        player.quitPlayer()


    
