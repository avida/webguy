#!/usr/bin/python3
import subprocess
import os
import threading, time
import json

def runCommand(cmd):
   p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
   return p.communicate()

class DirFetcher(threading.Thread):
   def __init__(self):
      self.TIMEOUT = 3
      self.EMPTY_DIR = ([],[])
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
         Exception.__init__(self,msg)
        
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
          dirs, files = self.getDirsAndFiles(full_path);
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

if __name__ == "__main__":
   print(LoadFile("dlna.py"))
   exit(0)
   browser = FileBrowser("/mnt/nfs")
   while True:
     print (browser.processItemOnFS('.'))
     time.sleep(1)
