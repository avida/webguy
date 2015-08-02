#!/usr/bin/python3
import http.client
from urllib.parse import urlparse
import json
token = "3954ccb7fcb40fe2612c15457f"
items_per_page = 10
drible_host = "api.dirble.com"
url_template = "/v2/stations?page=%d&per_page=%d&token=%s"
station_template = "/v2/station/%d?token=%s"

class DirbleConnection:
    def __init__(self, host):
        self.host = host
        self.c = None
        self.pages = None
    def getData(self, req): 
        if not self.c:
            print("connecting " , self.host)
            self.c = http.client.HTTPConnection(self.host)
            print("connected")
        self.c.request("GET", req)
        resp = self.c.getresponse()
        try:
            self.pages = int(resp.getheader('X-Total-Pages'))
        except Exception:
            pass
        if resp.status == 302:
            location = resp.getheader("location")
            print("new lock = ", location)
            self.c = None
            self.host = urlparse(location).netloc
            return self.getData(req)
        elif resp.status != 200:
            return "{'error':'bad response %d'}" % resp.status
        else:
            return resp.read().decode("ascii")
            
class Dirble:
    def __init__(self):
        self.current_page = 1
        self.pages = 0
        self.connection = None
        self.cache = None

    def createRequest(self):
        return url_template % (self.current_page, items_per_page, token)
   
    def createGetStationRequest(self, station_id):
        return station_template % (station_id, token)

    def getData(self, req):
        try:
            if not self.connection:
                self.connection = DirbleConnection(drible_host)
            return json.loads( self.connection.getData(req) )
        except http.HTTPException:
            self.connection = DirbleConnection(drible_host)
            return []

    def loadList(self):
        lst = self.getData(self.createRequest())
        if not self.pages:
            self.pages = self.connection.pages
        if len(lst) != 0:
           self.cache = lst
        return lst

    def getStationInfo(self, station_id):
        if self.cache and station_id in self.cache:
            return self.cache[station_id]
        r = self.createGetStationRequest(station_id)
        print(r)
        return self.getData(self.createGetStationRequest(station_id))

    def NextPage(self):
        if self.pages and self.current_page < self.pages:
            self.current_page +=1
            return True 
        return False

    def PrevPage(self):
        if self.current_page > 1:
            self.current_page -=1
            return True
        else:
            return False

if __name__ == "__main__":
    d = Dirble()
    print(str(d.loadList()))
    d.NextPage()
    lst = d.loadList()
    for i in lst:
        print (i["streams"])
