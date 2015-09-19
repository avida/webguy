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
    def process(self, cmd):
        if not self.last:
            if self.processFunc(cmd):
                self.last = time.time()
        else:
            elapsed = time.time() - self.last
            if elapsed >= COMMAND_INTERVAL:
                if self.processFunc(cmd):
                    self.last = time.time()

    def processFunc(self, cmd):
        if 'ff000f' in cmd:
            con = http.client.HTTPConnection('127.0.0.1')
            con.request("GET", "/srv/socket/switch/4")
            r = con.getresponse()
            return True
        return False
    
class UARTThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
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
