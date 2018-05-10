#!/usr/bin/python3
from nrf24 import NRF24
from plumbum import cli
from queue import Queue, Empty
from threading import Thread
import os
import redis
import time
import logging

logger = logging.getLogger("nrf service")
logging.basicConfig(level=logging.DEBUG)

NRF_RECEIVE_CHANNEL = "nrf.receive"
NRF_SEND_CHANNEL = "nrf.send"
INTERRUPT_PIN = 2
NRF_DATA_PIN = 17
NRF_LOAD_SIZE = 8


def initNRF():
    radio = NRF24()
    radio.begin(0, 0, NRF_DATA_PIN, INTERRUPT_PIN)
    radio.setPayloadSize(NRF_LOAD_SIZE)
    radio.setChannel(0x2)
    radio.setCRCLength(NRF24.CRC_8)
    radio.setDataRate(NRF24.BR_2MBPS)
    radio.write_register(NRF24.RF_SETUP, 0xf)
    radio.write_register(NRF24.EN_RXADDR, 0x3)
    radio.openReadingPipe(0, [0xe7, 0xe7, 0xe7, 0xe7, 0xe7])
    return radio


class App(cli.Application):
    def subThr(self):
        sub = self.r.pubsub()
        sub.subscribe([NRF_SEND_CHANNEL])
        for msg in sub.listen():
            if msg["type"] != "message":
                continue
            self.q.put(msg)

    @staticmethod
    def sendMesssage(radio, msg):
        radio.retries = 1
        radio.stopListening()
        body = int(msg["data"]).to_bytes(4, byteorder="little")
        body = [42] + list(body) + [0] * 3
        logger.debug(body)
        if radio.write(body):
            logger.info("sent")
        else:
            logger.info("failed")
        radio.startListening()

    def main(self, *arg):
        if not arg:
            return
        try:
            if arg[0] == "run":
                self.r = redis.Redis()
                # Check redis connection
                self.r.get(None)
                logger.info("run nrf server")
                self.q = Queue()
                radio = initNRF()
                radio.startListening()
                radio.printDetails()
                t = Thread(target=lambda: self.subThr())
                t.start()
                while(True):
                    while not radio.available([0], False):
                        try:
                            if self.q.qsize() != 0:
                                msg = self.q.get_nowait()
                                logger.debug(msg)
                                App.sendMesssage(radio, msg)
                            time.sleep(0.02)
                        except Empty:
                            logger.error("error getting item")
                    recv_buff = []
                    radio.read(recv_buff)
                    self.r.publish(NRF_RECEIVE_CHANNEL, bytes(recv_buff))
            elif arg[0] == "send":
                r = redis.Redis()
                if len(arg) >= 2:
                    code = arg[1]
                else:
                    code = 0
                r.publish(NRF_SEND_CHANNEL, code)
            elif arg[0] == "recv":
                r = redis.Redis()
                sub = r.pubsub()
                sub.subscribe(NRF_RECEIVE_CHANNEL)
                for msg in sub.listen():
                    if msg["type"] == "message":
                        data = msg["data"]
                        logger.info(list(data))
                        logger.info("received packet of type {}, value: {}".format(
                            data[0], int.from_bytes(data[1:5], byteorder="little")))
            else:
                logger.error("unknown argument")
        except KeyboardInterrupt:
            logger.error("Interrupt received")
            os._exit(0)
        except redis.exceptions.ConnectionError:
            logger.error("Error connecting to redis")
            os._exit(0)

App.run()
