'''
Functions for creating and parsing binary strings.
'''
import struct

def pack_binary_string(format, *args):
    try:
        s = struct.Struct(format)
        packet = s.pack(*args)
        return packet
    except ValueError as e:
        print e

def unpack_binary_string(format, packet):
    try:
        s = struct.Struct(format)
        packet = s.unpack(packet)
        return packet
    except ValueError as e:
        print e

def read_binary_file(file_name):
    ''' Reads bytes from given file, returns binary string ''' 
    with open(file_name, "rb") as f:
        data = f.read()
    return data 
