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

packet = 0

def nrfWrite():
    radio.retries = 1
    radio.stopListening()
    global packet 
    while(True):
        if radio.write("2" * 8):
            packet += 1
        else:
            print("failed")
        print(radio.get_status())
        time.sleep(.001)


def nrfRead():
   global packet
   while(True):
        while not radio.available([0], False):
            time.sleep(0.001)
        recv_buff = []
        time.sleep(0.002)
        radio.read(recv_buff)
        print("received packet: " +  str(recv_buff))

        packet += 1

def pingpong():
    global packet
    while(True):
        while not radio.available([0], False):
            time.sleep(0.001)
        #print("recv")
        packet += 1
        recv_buff = []
        radio.read(recv_buff)
        radio.stopListening()
        retry = 0
        while not radio.write("PONG"):
            #print("retry")
            retry += 1
        radio.startListening()

def cntr():
    global packet
    while(True):
        time.sleep(1)
        print("packets: {}".format( packet ))
        packet = 0
t = Thread(target=cntr) 
#t.start()

#pingpong()
nrfRead()
#nrfWrite()


