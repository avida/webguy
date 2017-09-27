#!/usr/bin/python3
import subprocess
import os
import threading
import time
import json
import datetime
import math


def runCommand(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    return p.communicate()


class DirFetcher(threading.Thread):

    def __init__(self):
        self.TIMEOUT = 3
        self.EMPTY_DIR = ([], [])
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.dir = self.EMPTY_DIR
        self.cond = threading.Condition()
        self.is_running = False

    def run(self):
        self.is_running = True
        try:
            if os.path.isfile(self.path):
                self.dir = None
            else:
                _, d, f = next(os.walk(self.path))
                self.dir = d, f
        except Exception:
            self.dir = None

        self.is_running = False
        self.cond.acquire()
        self.cond.notify()
        self.cond.release()

    def Fetch(self, path):
        if self.is_running:
            return self.EMPTY_DIR
        self.__init__()
        self.path = path
        self.start()
        self.cond.acquire()
        self.cond.wait(self.TIMEOUT)
        self.cond.release()
        if self.dir == None:
            raise FileBrowser.NotADirException("Is not a dir")
        return self.dir


class FileBrowser:

    class NotADirException(Exception):

        def __init__(self, msg):
            Exception.__init__(self, msg)

    def __init__(self, path, windows_path=False):
        self.dir_path = path
        self.fetcher = DirFetcher()
        if windows_path:
            self.path_pattern = "%s\%s"
        else:
            self.path_pattern = "%s/%s"

    def getDirsAndFiles(self, path):
        return self.fetcher.Fetch(path)

    def processItemOnFS(self, path):
        full_path = self.path_pattern % (self.dir_path, path)
        try:
            dirs, files = self.getDirsAndFiles(full_path)
            dirs.sort()
            files.sort()
            data = json.dumps({"dirs": dirs, "files": files})
            return data
        except UnicodeEncodeError:
            return "Error decoding path characters. Probably system locale is not an uniconde"


def LoadFile(filename):
    if not os.path.isfile(filename):
        return None
    with open(filename, "r") as f:
        return f.read()


def WriteToFile(filename, data):
    with open(filename, "w") as f:
        f.write(data)


def SystemUptime():
    def getTimedelta(time):
        return datetime.timedelta(seconds=math.floor(float(time)))
    uptime, idletime = LoadFile('/proc/uptime').split()
    uptime = getTimedelta(uptime)
    return uptime

def ConnectionRefusedHandler(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ConnectionRefusedError:
            return makeErrorResponse("no connection  :(")
    # flask url dispatcher relies on __name__ attribute
    # to make sure request handler is unique
    wrapper.__name__ = f.__name__
    return wrapper

def makeErrorResponse(msg):
    return json.dumps({'error': str(msg)})

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
        
if __name__ == "__main__":
    browser = FileBrowser("./")
    print(browser.processItemOnFS('.'))
