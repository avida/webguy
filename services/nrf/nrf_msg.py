import struct

def pack_message(value):
   pkt = struct.pack("BBhI", 42, 1, 2, value)
   return pkt

def unpack_message(raw_msg):
    return None

