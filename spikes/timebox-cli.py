#!/usr/bin/python3

import logging
import random
import time
from itertools import product
from plumbum import cli
from timebox import Timebox, Image

logger = logging.getLogger("timebox-cli")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

tb_logger = logging.getLogger("timebox")
tb_logger.setLevel(logging.INFO)
tb_logger.addHandler(logging.StreamHandler())
 
class App(cli.Application):
    address = cli.SwitchAttr(["-a", "--address"], str, help="Bluetooth address")
    data = cli.SwitchAttr(["-d", "--data"], str, help="raw data to send")

    def main(self, operation):
        device = Timebox(self.address)
        logger.info("run: addrss: {}, oper: {}".format(self.address, operation))
        logger.info("connecting")
        device.connect()
        if operation == "raw":
            if not self.data:
                logger.error("Please specify data")
                return
            device.send_raw(self.data)
        elif operation == "image":
            cntr = 11
            while True:
                img = Image()
                #img.fillImage(0,0,15)
                for x,y in product(range(0,11), range(0,11)):
                    g = (x + cntr) % 22
                    g = g if g < 11 else 22 - g
                    img.setPixel(
                    x, y,
                    0,g,5)
                data = img.data
                device.sendImage(data)
                time.sleep(.2)
                cntr+=1

        time.sleep(74)


if __name__ == "__main__":
    App.run()

