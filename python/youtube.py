#!/usr/bin/python3
from web_backend import ServiceConnection
import urllib.parse
import json

DEV_KEY = "AIzaSyDaMq7oWT-ZSTAGswiNwCLh864QhL9dfUw"
YOUTUBE_HOST = "content.googleapis.com"
API_PATH = 'youtube/v3/'


class YouTube(ServiceConnection):

    def __init__(self):
        ServiceConnection.__init__(self, YOUTUBE_HOST, https=True)

    def search(self, q, token = None, type = None):
        vars = {"part": "id,snippet", "q": q,
                "maxResults": 5}
        if type:
            vars["type"] = type
        print(type)
        if token:
            vars["pageToken"] = token
        print(str(vars))
        url = self.buildUrl("search", vars)
        return json.loads(self.getData(url))

    def buildUrl(self, method, params):
        params["key"] = DEV_KEY
        url = "https://" + YOUTUBE_HOST + '/' + API_PATH + method
        return url + '?' + urllib.parse.urlencode(params)

if __name__ == "__main__":
    yt = YouTube()
    res = yt.search("eminem")
    print(json.dumps(res, indent=1))
    token = res["nextPageToken"]
    res = yt.search("eminem", token)
    print(json.dumps(res, indent=1))
