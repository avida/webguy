#! /usr/bin/python3
import serial
import threading
import time
import http.client

COMMAND_INTERVAL = 5
port = serial.Serial("/dev/ttyAMA0", baudrate=115200)

def readlineCR(port):
    rv = b''
    while True:
        ch = port.read()
        rv += ch
        if ch==b'\n' or ch==b'':
            return rv.decode('ascii').strip()

class CommandProcessor:
    def __init__(self):
        self.last = False
        self.interval = 0

    def process(self, cmd):
        if not self.last:
            self.interval = self.processFunc(cmd)
            self.last = time.time()
        else:
            elapsed = time.time() - self.last
            if elapsed >= self.interval:
                self.interval = self.processFunc(cmd)
                self.last = time.time()
    def sendRequest(self, req):
        con = http.client.HTTPConnection('127.0.0.1')
        con.request("GET", req)
        r = con.getresponse()

    def processFunc(self, cmd):
        if 'ff000f' in cmd:
            self.sendRequest("/srv/socket/switch/17")
            return 5
        elif '6509af' in cmd:
            self.sendRequest("/srv/player/forward")
            return 1
        elif 'd002ff' in cmd:
            self.sendRequest("/srv/player/pplay")
            return 1
        elif 'e501af' in cmd:
            self.sendRequest("/srv/player/backward")
            return 1
        elif '9f060f' in cmd:
            self.sendRequest("/srv/radio/stop")
        return 0
    
class UARTThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
    def run(self):
        cp = CommandProcessor()
        while True:
            line = readlineCR(port)
            cp.process(line)

def startListen():
    t = UARTThread()
    t.start()
    return t
if __name__ == "__main__":
    startListen().join();
