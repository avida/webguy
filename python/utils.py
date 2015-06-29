#!/usr/bin/python3
import subprocess
def runCommand(cmd):
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
  return p.communicate()