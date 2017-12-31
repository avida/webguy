#!/usr/bin/python3
from nrf24 import NRF24
import time
from functools import reduce
from threading import Thread

radio = NRF24()
radio.begin(0,0, 17, 2)
radio.setPayloadSize(8)
radio.setChannel(0x2)
radio.setCRCLength(NRF24.CRC_8) 
radio.setDataRate(NRF24.BR_2MBPS)
radio.write_register(NRF24.RF_SETUP, 0xf) 
radio.write_register(NRF24.EN_RXADDR, 0x3) 

radio.openReadingPipe(0, [0xe7, 0xe7, 0xe7, 0xe7, 0xe7])

radio.startListening()

radio.printDetails()

def nrfWrite():
    while(True):
        radio.write("2" * 8)
packet = 0
def nrfRead():
    def cntr():
        global packet
        while(True):
            time.sleep(1)
            print("packets: {}".format( packet ))
            packet = 0
    t = Thread(target=cntr) 
    global packet
    t.start()
    while(True):
        while not radio.available([0], True):
            time.sleep(0.001)
        recv_buff = []
        time.sleep(0.002)
        radio.read(recv_buff)
        packet += 1

def pingpong():
    while(True):
        while not radio.available([0], True):
            pass
        print("recv")
        recv_buff = []
        radio.read(recv_buff)
        radio.stopListening()
        radio.write("Pong")
        radio.startListening()

pingpong()


