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
        print ("starting player: ", cmd )
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

    def quitPlayer(self):
        self.sendKey(b'q')
        time.sleep(3)

    def pause(self):
        self.sendKey(b'p')

    def startStream(self, url):
        cmd = "livestreamer --retry-open 3 \"%s\" best --yes-run-as-root --player \"omxplayer\" --fifo" % url
        print (cmd)
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        

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
        player.startStream('https://www.youtube.com/watch?v=Le4LsePzn4M')
        while True:
            line = player.proc.stdout.readline()
            if line:
                print( line )
        player.startPlayer('/root/Fargo.DVDRip_0dayTeam.avi')
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
    
