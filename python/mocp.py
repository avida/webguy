#!/usr/bin/python
from utils import runCommand
import re
vol_re = re.compile('\sMono.+\[(\d+)%\]')
amixer_vol_template = "amixer set PCM {}%"
class MOCP:
    def __init__(self): 
        self.vol = MOCP.volume()

    def parseVolume(out):
        s = vol_re.search(out)
        if s:  
            return int(s.group(1))
        return -1

    def runMOCP(args):
        return runCommand("mocp {} 2>/dev/null".format(args))[0].decode("ascii")

    def volume():
        cmd_out = runCommand("amixer")
        return MOCP.parseVolume(cmd_out[0].decode("ascii"))

    def volumeUp(self):
        if self.vol== -1:
            self.vol= MOCP.volume()
        out = MOCP.setVolume(self.vol+1)
        self.vol = MOCP.parseVolume(out)

    def volumeDown(self):
        if self.vol== -1:
            self.vol= MOCP.volume()
        out = MOCP.setVolume(self.vol-1)
        self.vol = MOCP.parseVolume(out)

    def setVolume(val): 
        return runCommand(amixer_vol_template.format(val))[0].decode("ascii")

    def getCurrentTitle():
        return MOCP.runMOCP("-Q %title").strip()

    def play(item):
        return MOCP.runMOCP("-c -a {} -p".format(item))

    def stop():
        return MOCP.runMOCP("-s")

if __name__ == "__main__":
    print(MOCP.play("http://sc9.radioseven.se:8500"))
    MOCP.stop()
