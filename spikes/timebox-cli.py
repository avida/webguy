#!/usr/bin/python3

import logging
import random
import time
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
            while True:
                img = Image()
                #img.fillImage(0,0,15)
                """
                img.fillImage(
                random.randint(0,15),
                random.randint(0,15),
                random.randint(0,15))
                """
                img.setPixel(
                random.randint(0,10),
                random.randint(0,10),
                0,15,0)
                #data =  random.sample(range(0,256), 182)
                data = img.data
                device.sendImage(data)
                time.sleep(.2)

        time.sleep(74)


if __name__ == "__main__":
    App.run()

