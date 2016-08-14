#!/usr/bin/python3
import sched
import threading
import time
import datetime
from datetime import timedelta
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


class TimePattern:
    def __init__(self, **kwargs):
        self.tuple_format = ("year","month","day","hour", "minute")
        self.tuple_index  = dict(zip(self.tuple_format, range(0, len(self.tuple_format))))
        def red(accum, x):
            accum.append(kwargs.get(x,0))
            return accum
        import functools
        self.at = tuple(functools.reduce(red, self.tuple_format, []))

    def __getattr__(self, attr):
        return self.at[self.tuple_index[attr]]

    def getMaxSignVal(self):
        max_sign_val = next((item for item
                             in range(0, len(self.at)) if self.at[item] !=0),
                             -1)
        return max_sign_val

    def getSignificantValues(self):
        max_sign_val = self.getMaxSignVal()
        min_sign_val= next((item for item
                            in reversed(range(0, len(self.at))) if self.at[item] !=0),
                            len(self.tuple_format))

        return self.tuple_format[max_sign_val: min_sign_val+1], \
                                 self.tuple_format[min_sign_val+1:]

    def getAnchorDate(self, current_time, future=None):
        time_args = {}
        max_sign_val = self.getMaxSignVal()
        for i in range(0 ,max_sign_val):
            attr_name = self.tuple_format[i]
            time_args[attr_name] = getattr(current_time, attr_name)
        for i in range(max_sign_val, len(self.tuple_format)):
            attr_name = self.tuple_format[i]
            time_args[attr_name] = self.at[i]
        anch_date = datetime.datetime(**time_args)
        if future:
            if future == "month":
                time_args[future] += 1
                anch_date = datetime.datetime(**time_args)
            else:
                anch_date += timedelta(**{future+"s":1})
        return anch_date

    def getSignificantTimeDelta(self, current_time):
        values = self.getSignificantValues()
        isFit = all([getattr(current_time, m) == getattr(self, m)
                     for m in values[0]] )
        if isFit:
            ar = {}
            for item in values[1]:
                ar[item + "s"] = getattr(current_time, item)
            return timedelta(**ar)
        else:
            anch_date = self.getAnchorDate(current_time)
            delta = current_time - anch_date
            if anch_date < current_time:
                max_sign_val = self.getMaxSignVal()
                fut_val = self.tuple_format[max_sign_val - 1]
                anch_date = self.getAnchorDate(current_time, future = fut_val)
            return anch_date - current_time

    def getTimeDelta(self):
        values = self.getSignificantValues()[0]
        args = {}
        for arg in values:
            args[arg+"s"] = getattr(self, arg)
        return timedelta(**args)


class RepetativePattern:
    def __init__(self, start_time = None):
        self.start_time = start_time
        self.period = 0
        self.at = []

    def EveryHour(self, hour):
        return self.EveryMinute(60 * hour)

    def EveryMinute(self, minute):
        self.EverySecond(60 * minute)

    def EverySecond(self, second):
        self.period = second
        return self

    def At(self, **timed):
        self.at.append(TimePattern(**timed))
        return self

    def FromTime(self, time):
        self.start_time = time
        return self

    """
    Returns number of second upcoming event scheduled in
    """
    def UpcomingEvent(self, current_time):
        if not self.start_time:
            return None
        if not len(self.at) and not self.period:
            return None

        if (self.start_time > current_time):
            return self.start_time - current_time
        if self.period:
            diff = current_time - self.start_time
            return timedelta(seconds= diff.seconds % self.period)
        upcoming_events = []
        for date in self.at:
            event = date.getSignificantTimeDelta(current_time)
            upcoming_events.append(event)
        print(upcoming_events)
        upcoming_events.sort()
        return upcoming_events[0]

class RepetativeEvent:

    def __init__(self, scheduler):
        self.sched = scheduler

    def Schedule(self, pattern, f):
        self.f = f
        self.pattern = pattern

    def __call__(self, *args, **kwargs):
        self.f(args, kwargs)
        self.reschedule()
        pass

    def Reschedule(self):
        pass


@Action("print_time")
def print_time(id, **kwargs):
    print("Time is", time.time(), " ", id, "  ", datetime.datetime.now())


@Action("print_datetime")
def print_datetime(arg, **kwargs):
    print("datetime: " + arg)

if __name__ == "__main__":
    import unittest

    @unittest.skip("longest test")
    class SchedulerTest(unittest.TestCase):

        def test_sched(self):
            print(time.time())
            a = Scheduler()
            a.enter(4, print_time, 5, he="heee")
            print(a.list)
            #a.enterFromDate(datetime.datetime.now() + datetime.timedelta(hours=3), print_datetime, "alaram!!", other="oth" )
            try:
                a.start()
                time.sleep(10)
            except KeyboardInterrupt:
                print("interrupted")
            finally:
                a.UpdateSettings()
            print(time.time())


    @unittest.skip("not implemented yet")
    class PickleTest(unittest.TestCase):

        def test_pickle(self):
            import pickle
            print ("Pickle test")
            pattern = RepetativePattern(datetime.datetime.now())
            pattern.At(hours=22)
            pattern.At(hours=8)
            print (pickle.dumps(pattern))

    class RepetativePatternTest(unittest.TestCase):

        test_time = datetime.datetime(year=2016, month=10, day=20, hour=22)
        test_time_month_end = datetime.datetime(year=2016, month=10, day=31, hour=22)
        test_time_eoy = datetime.datetime(year=2016, month=12, day=31, hour = 23)

        def test_pattern(self):
            print("repetative pattern test")
            pattern = RepetativePattern(datetime.datetime.now() - timedelta(hours=5,minutes=59, seconds=13))
            pattern.EveryHour(4)
            print (pattern.UpcomingEvent(datetime.datetime.now()))

        def test_date(self):
            print("test date")
            pattern = RepetativePattern(RepetativePatternTest.test_time)
            pattern.At(hour=22)
            upcoming = pattern.UpcomingEvent(RepetativePatternTest.test_time - timedelta(hours = 1) )
            self.assertEqual(upcoming, timedelta(hours=1))

            upcoming = pattern.UpcomingEvent(RepetativePatternTest.test_time + timedelta(hours = 1) )
            self.assertEqual(upcoming, timedelta(hours=23))

            pattern = RepetativePattern(RepetativePatternTest.test_time_month_end)
            pattern.At(hour=22)
            upcoming = pattern.UpcomingEvent(RepetativePatternTest.test_time_month_end + timedelta(hours = 1) )
            self.assertEqual(upcoming, timedelta(hours=23))

            pattern = RepetativePattern(RepetativePatternTest.test_time_eoy)
            pattern.At(hour=22)
            pattern.At(hour=8)
            upcoming = pattern.UpcomingEvent(RepetativePatternTest.test_time_eoy)
            self.assertEqual(upcoming, timedelta(hours=9))
            upcoming = pattern.UpcomingEvent(RepetativePatternTest.test_time_eoy + timedelta(hours=10))
            self.assertEqual(upcoming, timedelta(hours=13))
            upcoming = pattern.UpcomingEvent(RepetativePatternTest.test_time_eoy + timedelta(hours=24))
            self.assertEqual(upcoming, timedelta(hours=9))


    class TimePatternTest(unittest.TestCase):

            curr_time = datetime.datetime(year=2016, month=10, day=20, hour=22)
            curr_time_end_of_month = datetime.datetime(year=2016, month=10, day=31, hour=22)
            curr_time_end_of_year = datetime.datetime(year=2016, month=12, day=31, hour=22)

            def test_basic(self):
                print ("Time pattern test")
                p = TimePattern (hour=23, minute=10)
                self.assertEqual(p.getSignificantValues()[0], ("hour","minute"))
                self.assertEqual(p.getSignificantValues()[1], ())

                p = TimePattern (day=20, hour=23)
                self.assertEqual(p.getSignificantValues()[0], ("day","hour"))
                tdelta = p.getSignificantTimeDelta(TimePatternTest.curr_time)
                self.assertEqual(tdelta, timedelta(hours=1))

                p = TimePattern (day=20, hour=21)
                self.assertEqual(p.getSignificantValues()[0], ("day","hour"))
                tdelta = p.getSignificantTimeDelta(TimePatternTest.curr_time)
                self.assertEqual(tdelta, timedelta(days=30, hours=23))

            def test_every_hour(self):
                p = TimePattern (hour=20)
                self.assertEqual(p.getSignificantValues()[0], ("hour",))
                tdelta = p.getSignificantTimeDelta(TimePatternTest.curr_time)
                self.assertEqual(tdelta, timedelta(hours=22))

                p = TimePattern (hour=8)
                tdelta = p.getSignificantTimeDelta(TimePatternTest.curr_time)
                self.assertEqual(tdelta, timedelta(hours=10))

                p = TimePattern (hour=21)
                self.assertEqual(p.getSignificantValues()[0], ("hour",))
                tdelta = p.getSignificantTimeDelta(TimePatternTest.curr_time)
                self.assertEqual(tdelta, timedelta(hours=23))

                p = TimePattern (hour=21)
                self.assertEqual(p.getSignificantValues()[0], ("hour",))
                tdelta = p.getSignificantTimeDelta(TimePatternTest.curr_time_end_of_month)
                self.assertEqual(tdelta, timedelta(hours=23))

                p = TimePattern (hour=21)
                self.assertEqual(p.getSignificantValues()[0], ("hour",))
                tdelta = p.getSignificantTimeDelta(TimePatternTest.curr_time_end_of_year)
                self.assertEqual(tdelta, timedelta(hours=23))

            def test_anchor_date(self):
                p = TimePattern(day=22)
                anch = p.getAnchorDate(TimePatternTest.curr_time)
                self.assertEqual(datetime.datetime(year=2016, month=10, day=22), anch)

                p = TimePattern(day=22)
                anch = p.getAnchorDate(TimePatternTest.curr_time, future="day")
                self.assertEqual(datetime.datetime(year=2016, month=10, day=23), anch)

                p = TimePattern(hour=22)
                anch = p.getAnchorDate(TimePatternTest.curr_time_end_of_month, future = "day")
                self.assertEqual(datetime.datetime(year=2016, month=11, day=1, hour=22), anch)

                p = TimePattern(hour=22)
                anch = p.getAnchorDate(TimePatternTest.curr_time_end_of_month, future = "day")
                self.assertEqual(datetime.datetime(year=2016, month=11, day=1, hour=22), anch)

                p = TimePattern(hour=22)
                anch = p.getAnchorDate(TimePatternTest.curr_time_end_of_year, future = "day")
                self.assertEqual(datetime.datetime(year=2017, month=1, day=1, hour=22), anch)
                print("anch: ", anch)

    unittest.main()
