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
                self.c.set_debuglevel(0)
                print("connected")
                return
            except Exception:
                print ("reconnecting")
                retry_count -= 1
        raise ConnectionRetriesiExceeded(self.retries)

    def getData(self, req, withHeaders = False, headers = None, data = None): 
        try:
            if not self.c:
                self.tryToConnect()
            request_retries = 3
            while  request_retries:
                try:
                    if data:
                        self.c.request("POST", req, body=data, headers=headers )
                    else:
                        if headers:
                           self.c.request("GET", req, headers=headers)
                        else:
                           self.c.request("GET", req)
                    resp = self.c.getresponse()
                    if resp.status != 200:
                        print ("bad response: " + str(resp.status))
                        return "Bad response"
                    data = resp.read().decode("utf-8")
                    if withHeaders:
                        return (data, resp.headers)
                    else:
                        return data
                # Broken pipe occures on https connection
                # Probably due to the python https implementation paticularities
                except (http.client.HTTPException, BrokenPipeError):
                    print ("retry request")
                    request_retries -= 1
                    self.tryToConnect()
        except ConnectionRetriesiExceeded:
            return "Cannot connect to " + self.host
        return "Cannot serve request"
