#!/usr/bin/python3
import subprocess
import os
import json

def runCommand(cmd):
   p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
   return p.communicate()

class FileBrowser:
   class NotADirException(Exception):
      def __init__(self, msg):
         Exception.__init__(self,msg)
        
   def __init__(self, path, windows_path=False):
      self.dir_path = path
      if windows_path:
         self.path_pattern = "%s\%s"
      else:
         self.path_pattern = "%s/%s"

   def getDirsAndFiles(path):
      _, d, f = next(os.walk(path))
      return d, f

   def processItemOnFS(self, path):
      full_path = self.path_pattern % (self.dir_path, path)
      try:
         if os.path.isfile(full_path):
             raise FileBrowser.NotADirException("Is not a dir")
         else:
             dirs, files = FileBrowser.getDirsAndFiles(full_path);
             dirs.sort()
             files.sort()
             data = json.dumps({"dirs": dirs, "files": files})
             return data
      except UnicodeEncodeError:
          return "Error decoding path characters. Probably system locale is not an uniconde"
if __name__ == "__main__":
   browser = FileBrowser("/root/share")
   print (browser.processItemOnFS('.'))
