#!/usr/bin/python3
import http.client
import json
import urllib
from web_backend import ServiceConnection

TWITCH_BASE_REQ = "kraken"
TWITCH_HOST = "api.twitch.tv"

class Twitch (ServiceConnection):
    def __init__(self):
        self.items_per_page = 11
        ServiceConnection.__init__(self, TWITCH_HOST, https=True)
    def getGames(self, page=0):
        js = json.loads(self.getData("/kraken/games/top?limit=%d&offset=%d" %
                        (self.items_per_page, page * self.items_per_page )))
        x = [ (x["game"]["name"], 
               x["viewers"],
               x["game"]["box"]["small"]) for x in js["top"] ]
        return x

    def searchStreams(self, game, page = 0):
        data = (self.getData("/kraken/streams?game=%s&limit=%d&offset=%d" % 
               (game, self.items_per_page, self.items_per_page * page )))
        try:
            js = json.loads(data)
            x = [ (x['channel']['display_name'], 
                   x['channel']['url'].replace("http://www.twitch.tv/", ""),
                   x['preview']['small'],
                   x['viewers']
                   ) for x in js["streams"] ]
            return x
        except ValueError as e:
            print ("Error parsing data: ", str(data))
            return "None"

if __name__ == "__main__":
    print("Twitch module")
    t = Twitch()
    for s in t.searchStreams("StarCraft%20II", 2):
        print(s)
