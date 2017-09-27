from flask_raspi import app
from flask import abort, request
import urllib.parse
import json
from youtube import YouTube

yt = YouTube()

@app.route("/youtube/search/<string:query>")
def youtubeSearch(query):
    try:
        js = yt.search(query, 
             token = request.args.get("token", None),
             type =  request.args.get("type", "video"))
    except Exception as e:
        return "not ok: " + str(e)
    items = [{
              "id": x["id"]["playlistId"] if "playlistId" in x["id"] else x["id"]["videoId"],
              "title": x["snippet"]["title"],
              "thumbnail": x["snippet"]["thumbnails"]["medium"]["url"],
              "published": x["snippet"]["publishedAt"]}
              for x in js["items"] 
              if x["id"]["kind"] == "youtube#video" or 
                 x["id"]["kind"] == "youtube#playlist"
            ]
    res = {"items": items}
    if "nextPageToken" in js:
        res["nextToken"] = js["nextPageToken"]
    if "prevPageToken" in js:
        res["prevToken"] = js["prevPageToken"]
    result = json.dumps(res)
    return result

@app.route('/youtube/<string:action>/<string:value>')
def youtubeAction(action, value):
    if action == "play":
        try:
            xbmc.openYoutubeVideo(value)
            return "ok"
        except IndexError:
            return "not ok"
    elif action == "playlist":
        try:
            xbmc.openYoutubeList(value)
            xbmc.StartPlaylist(1)
            return "ok"
        except IndexError:
            return "not ok"
    else:
        abort(404)

