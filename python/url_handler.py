#!/usr/bin/python3


class UrlDispatcher:

    def __init__(self):
        self.url_map = {}

    def addHandler(self, url,  handler):
        self.__addHandler(self.url_map, url.split('/')[1:], handler)

    def __addHandler(self, d, url, hndlr):
        if len(url) == 1:
            d[url[0]] = hndlr
        else:
            if not url[0] in d:
                d[url[0]] = {}
            self.__addHandler(d[url[0]], url[1:], hndlr)

    def dispatchUrl(self, url):
        return self.__dispathUrl(self.url_map, url.split('/')[1:])

    def __dispathUrl(self, d, url):
        if not url or not url[0] in d:
            return "Not Found"
        next_map = d[url[0]]
        if hasattr(next_map, '__call__'):
            return next_map(url[1:])
        else:
            return self.__dispathUrl(next_map, url[1:])


class UrlHandler:

    def __init__(self):
        pass

    def __call__(self, params):
        return "object called: " + str(params)

if __name__ == "__main__":
    dispathcer = UrlDispatcher()
    hnd = UrlHandler()
    dispathcer.addHandler("/www/srv", hnd)
    dispathcer.addHandler("/sdf/svv/wefefrv", hnd)
    print(str(dispathcer.url_map))
    print(dispathcer.dispatchUrl("/www/srv/dd"))
    print(dispathcer.dispatchUrl("/sdf/svv/wefefrv/sdf?gfg"))
