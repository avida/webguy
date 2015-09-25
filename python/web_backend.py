import http.client
import urllib


class ConnectionRetriesiExceeded(Exception):
    def __init__(self, retries):
        Exception.__init__(self, "Failed to connect after %d attemps" % retries)

class ServiceConnection:

    def __init__(self, host, https=False):
        self.host = host
        self.retries = 3 
        self.https = https
        self.c = None
    def tryToConnect(self):
        retry_count = self.retries
        while retry_count:
            try:
                print("connecting " , self.host)
                if self.https:
                    self.c = http.client.HTTPSConnection(self.host)
                else:  
                    self.c = http.client.HTTPConnection(self.host)
                self.c.set_debuglevel(1)
                print("connected")
                return
            except Exception:
                retry_count -= 1
        raise ConnectionRetriesiExceeded(self.retries)

    def getData(self, req, withHeaders = False): 
        print (req)
        try:
            if not self.c:
                self.tryToConnect()
            request_retries = 1
            while  request_retries:
                try:
                    self.c.request("GET", req )
                    resp = self.c.getresponse()
                    if resp.status != 200:
                        print ("bad responce: " + str(resp.status))
                        return
                    data = resp.read().decode("utf-8")
                    if withHeaders:
                        return (data, resp.headers())
                    else:
                        return data
                except http.client.HTTPException:
                    request_retries -= 1
                    self.tryToConnect()
        except ConnectionRetriesiExceeded:
            return "Cannot connect to " + self.host
        return "Cannot serve request"
