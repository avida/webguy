import socket
import logging
from binascii import unhexlify

logger = logging.getLogger("timebox")

class Timebox:
    def __init__(self, addr):
        self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.addr = addr

    def connect(self):
        self.sock.connect((self.addr, 4))

    def disconnect(self):
        self.sock.close()

    def send(self, package):
        logger.debug([hex(b) for b in package])
        self.sock.send(package)

    def send_raw(self, bts):
        self.send(unhexlify(bts))

    def sendImage(self, data):
        self.send(conv_image(data))

class Image:
    def __init__(self):
        self.data = None

    def setRGB(self, r, g, b, x, y):
        data1 = r& 0xf0 + g & 0x0f
        data2 = b

    def fillImage(self, r,g,b):
        first = True
        self.data = [0]
        for i in range(0, 121):
            if(first):
                self.data[-1] = (r)+(g<<4)
                self.data.append(b)
                first=False
            else:
                self.data[-1] += (r<<4)
                self.data.append(g+(b<<4))
                self.data.append(0)
                first=True

    def setPixel(self, x, y, r,g,b):
        if not self.data:
            self.fillImage(0,0,0)
        index = x +  11 * y
        first = index % 2 == 0
        index = int(index * 1.5)
        #logger.info("index: {}, first: {}".format(index, first))
        if first:
            self.data[index] = r + (g << 4)
            self.data[index+1] = self.data[index+1]&0xf0 + b
        else:
            self.data[index] = (self.data[index]&0x0f) + (r<<4)
            self.data[index+1] = g + (b<<4)
        
def conv_image(data):    
    # should be 11x11 px => 
    head = [0xbd,0x00,0x44,0x00,0x0a,0x0a,0x04]
    data = data
    ck1,ck2 = checksum(sum(head)+sum(data))
    
    msg = [0x01]+head+mask(data)+mask([ck1,ck2])+[0x02]
    return bytearray(msg)
    

def mask(bytes):
    _bytes = []
    for b in bytes:
        if(b==0x01):
            _bytes=_bytes+[0x03,0x04]
        elif(b==0x02):
            _bytes=_bytes+[0x03,0x05]
        elif(b==0x03):
            _bytes=_bytes+[0x03,0x06]
        else:
            _bytes+=[b]
        
    return _bytes

def checksum(s):
    ck1 = s & 0x00ff
    ck2 = s >> 8
    
    return ck1, ck2
