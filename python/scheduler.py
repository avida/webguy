#!/usr/bin/python3
import sched
import threading
import time
import datetime
from utils import LoadFile, WriteToFile
import json

SCHEDULER_SETTINGS = "scheduler.json"


class SchedulerSettings:

    def __init__(self):
      
        self.clearEvents()

    def clearEvents(self):
        self.data = {"events": {}}

    def Load(self):
        fileData = LoadFile(SCHEDULER_SETTINGS)
        if fileData:
            try:
                fileData = json.loads(fileData)
                self.data = fileData
            except Exception as e:
                print(str(e))

    def Save(self):
        WriteToFile(SCHEDULER_SETTINGS, json.dumps(self.data, indent=2))

    def AddEvent(self, event):
        self.data["events"][event.time] =  \
            {"priority": event.priority,
             "action": event.action.serialize(),
             "argument": event.argument,
             "kwargs": event.kwargs}


class Scheduler (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.s = sched.scheduler(time.time, time.sleep)
        self.settings = SchedulerSettings()
        self.settings.Load()
        self.LoadSettings()

    def run(self):
        print("thread running")
        while True:
            deadline = self.s.run(blocking=False)
            time.sleep(1)

    def enterFromDate(self, date, handler, *args, **kwargs):
        seconds_since_epoch = time.mktime(date.timetuple())
        self.s.enterabs(seconds_since_epoch, 1, handler,
                        argument=args, kwargs=kwargs)

    def enter(self, timeout, handler, *args, **kwargs):
        self.s.enter(timeout, 1, handler, argument=args, kwargs=kwargs)

    def enterabs(self, timeout, handler, *args, **kwargs):
        self.s.enterabs(timeout, 1, handler, argument=args, kwargs=kwargs)

    def LoadSettings(self):
        for event in self.settings.data["events"]:
            event_data = self.settings.data["events"][event]
            self.enterabs(float(event), eval(
                event_data["action"]), *event_data["argument"], **event_data["kwargs"])

    @property
    def list(self):
        lst = []
        for e in self.s.queue:
            lst.append("{0}: {1}".format(
                datetime.datetime.fromtimestamp(
                    e.time).strftime("%d/%m, %H:%M:%S"),
                e.action.serialize()))
        return lst

    def UpdateSettings(self):
        self.settings.clearEvents()
        for e in self.s.queue:
            self.settings.AddEvent(e)
        self.settings.Save()


class Action:

    def __init__(self, desc=""):
        self.desc = desc

    def __call__(self, f):
        class Wrapper:

            def __init__(self, f, desc):
                self.f = f
                self.desc = desc

            def serialize(self):
                return self.desc

            def __call__(self, *args, **kwargs):
                print("Performing action ", self.desc)
                return self.f(*args, **kwargs)

        return Wrapper(f, self.desc)


@Action("print_time")
def print_time(id, **kwargs):
    print("Time is", time.time(), " ", id, "  ", datetime.datetime.now())


@Action("print_datetime")
def print_datetime(arg, **kwargs):
    print("datetime: " + arg)

print(time.time())
a = Scheduler()
a.enter(4, print_time, 5, he="heee")
print(a.list)
#a.enterFromDate(datetime.datetime.now() + datetime.timedelta(hours=3), print_datetime, "alaram!!", other="oth" )
try:
    a.start()
    time.sleep(50)
except KeyboardInterrupt:
    print("interrupted")
finally:
    a.UpdateSettings()
print(time.time())
