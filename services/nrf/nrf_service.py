#!/usr/bin/env python3
from nrf24 import NRF24
from plumbum import cli
import redis
import nrf_msg

NRF_RECEIVE_CHANNEL = "nrf.receive"
NRF_SEND_CHANNEL = b"nrf.send"
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
    radio.openWritingPipe([0xe7, 0xe7, 0xe7, 0xe7, 0xe7])
    radio.printDetails()
    return radio

class App(cli.Application):
    RETRY_ATTEMPTS = 10

    def __init__(self, *args):
        self.radio = initNRF()
        self.r = redis.Redis()
        super().__init__(*args)

    def radio_send_msg(self, msg):
        self.radio.stopListening()
        for _ in range(0, self.RETRY_ATTEMPTS):
            print("Sending message")
            if self.radio.write(msg):
                break
        
    def main(self):
        print("Hi")
        sub = self.r.pubsub()
        sub.subscribe(NRF_SEND_CHANNEL)
        for msg in sub.listen():
            try:
                if msg["channel"] == NRF_SEND_CHANNEL and msg["type"] == 'message':
                    val = int(msg["data"])
                    msg = nrf_msg.pack_message(val)
                    print(msg)
                    self.radio_send_msg(msg)
                else:
                    print(msg)
            except ValueError as e:
                print(f"Error processing message {msg}")

App.run()
