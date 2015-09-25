#!/usr/bin/python3
import http.client
import json
import urllib
from web_backend import ServiceConnection

TWITCH_BASE_REQ = "kraken"
TWITCH_HOST = "api.twitch.tv"

class Twitch (ServiceConnection):
    def __init__(self):
        self.items_per_page = 10
        ServiceConnection.__init__(self, TWITCH_HOST, https=True)
    def getGames(self, page=0):
        js = json.loads(self.getData("/kraken/games/top?limit=%d&offset=%d" %
                        (self.items_per_page, page * self.items_per_page )))
        x = [ (x["game"]["name"], x["viewers"]) for x in js["top"] ]
        return x

    def searchStreams(self, game, page = 0):
        js = json.loads(self.getData("/kraken/search/streams?q=%s&limit=%d&offset=%d" % 
                        (urllib.parse.quote(game), self.items_per_page, self.items_per_page * page )))
        x = [ (x['channel']['display_name'], x['channel']['url'].replace("http://www.twitch.tv/", "")) for x in js["streams"] ]
        return x

if __name__ == "__main__":
    print("Twitch module")
    t = Twitch()
    for s in t.searchStreams("StarCraft II", 2):
        print(s)
