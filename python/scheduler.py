#!/usr/bin/python3
import sched, threading
import time

class Scheduler (threading.Thread):
   def __init__(self): 
      threading.Thread.__init__(self)
      self.setDaemon(True)
      self.s = sched.scheduler(time.time, time.sleep)

   def run(self):
      print ("thread running")
      while True:
         deadline = self.s.run(blocking=True)
         if not deadline:
            print ("scheduler is done")
            break

class Action:
   def __init__(self, desc=""):
      self.desc = desc

   def __call__(self, f):
      def inner(*args):
         print ("Performing action ", self.desc)
         f(*args)
      return inner

@Action("alarmclock")
def print_time():
   print("Time is", time.time()) 

print (time.time())
a = Scheduler()
a.s.enter(2, 1, print_time)
try:
   a.start()
   time.sleep(1)
   e = a.s.enter(2, 1, print_time)
   print ("sleep")
   lst = a.s.queue
   print (lst)
   time.sleep(5)
except KeyboardInterrupt:
   print ("interrupted")
print ("bb")
