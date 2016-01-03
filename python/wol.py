#!/usr/bin/python3

"""
Small module for use with the wake on lan protocol.

"""

from __future__ import absolute_import
from __future__ import unicode_literals

import socket
import struct
import threading
import time
BROADCAST_IP = '255.255.255.255'
DEFAULT_PORT = 9
new_intel = '00:1C:C0:05:F2:63'
class WOLThread(threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)
      self.stop=False
      self.mac = new_intel
      self.daemon = True
   def Stop(self):
      self.stop = True
   def run(self):
      time.sleep(3)
      if not self.stop:
         send_magic_packet(self.mac)
         print('sending wol packet')

def create_magic_packet(macaddress):
    """
    Create a magic packet which can be used for wake on lan using the
    mac address given as a parameter.

    Keyword arguments:
    :arg macaddress: the mac address that should be parsed into a magic
                     packet.

    """
    if len(macaddress) == 12:
        pass
    elif len(macaddress) == 17:
        sep = macaddress[2]
        macaddress = macaddress.replace(sep, '')
    else:
        raise ValueError('Incorrect MAC address format')

    # Pad the synchronization stream
    data = b'FFFFFFFFFFFF' + (macaddress * 20).encode()
    send_data = b''

    # Split up the hex values in pack
    for i in range(0, len(data), 2):
        send_data += struct.pack(b'B', int(data[i: i + 2], 16))
    return send_data


def send_magic_packet(*macs, **kwargs):
    """
    Wakes the computer with the given mac address if wake on lan is
    enabled on that host.

    Keyword arguments:
    :arguments macs: One or more macaddresses of machines to wake.
    :key ip_address: the ip address of the host to send the magic packet
                     to (default "255.255.255.255")
    :key port: the port of the host to send the magic packet to
               (default 9)

    """
    packets = []
    ip = kwargs.pop('ip_address', BROADCAST_IP)
    port = kwargs.pop('port', DEFAULT_PORT)
    for k in kwargs:
        raise TypeError('send_magic_packet() got an unexpected keyword '
                        'argument {!r}'.format(k))

    for mac in macs:
        packet = create_magic_packet(mac)
        packets.append(packet)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.connect((ip, port))
    for packet in packets:
        sock.send(packet)
    sock.close()
if __name__ == '__main__':
    send_magic_packet(new_intel)
