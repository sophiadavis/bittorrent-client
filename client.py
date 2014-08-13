'''
    UDP socket client
'''
import binascii
import bitstring
import errno
import random
import socket
import struct  
import sys
import time

def main():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(0)
        print 'Socket created.'
    except socket.error:
        print 'Could not create socket'
        sys.exit()
    
#     host = 'projects.sourceforge.net';
#     port = 2710;
#     host = 'tracker.istole.it'
#     port = 80
    host = 'thomasballinger.com';
    port = 6969;
    
    while(1):                 
        connection_id = 41727101980 # as64 bit integer (random?)
        action = 0 # 32 bit integer -- 0 for connect -- OFFSET 8
        transaction_id = random.getrandbits(31) # 32 bit int -- OFFSET 12
        
        s = struct.Struct('>qii')
        struct_connection_packet = s.pack(connection_id, action, transaction_id) # > for big endian, q for 64 bit int, i for 32 bit int
                 
        connection_packet = binascii.hexlify(struct_connection_packet)
        
        print "struct connection packet: " + struct_connection_packet
        print "size " + str(struct.calcsize('>qii'))
        print "connection packet: " + str(connection_packet)
        
        print "------"
        
        num = "uintbe:64={0}".format(connection_id)
        f = bitstring.BitArray(num)
        f.append("uintbe:32={0}".format(action)) 
        f.append("uintbe:32={0}".format(transaction_id))
        
        print f
        print len(f)
        print f.tobytes()
        
        print "------"
        
#         response = send_packet_to_tracker(sock, host, port, f.tobytes()) nothing
        response, address = send_packet_to_tracker(sock, host, port, connection_packet)
        print "Response: " + str(response)

def send_packet_to_tracker(sock, host, port, packet):
    
    sock.sendto(packet, (host, port))
    print 'Packet sent.'
    
    for n in range(8):
        try:
            print "trying"
            response, address = sock.recvfrom(10*1024)
            return response, address
            
        except socket.error:
            print 'excepting'
#           if response is -1: # LESS THAN 16 bytes, or transaction id is incorrect, or action is incorrect
            time.sleep(1)#15 * 2**n)
            sock.sendto(packet, (host, port))
            

if __name__ == '__main__':
    main()