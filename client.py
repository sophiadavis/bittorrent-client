'''
    UDP socket client
'''
import binascii
import random
import socket
import struct  
import sys
import time

# class Client:
#     def __init__(self):
#         self.connection_id = 4497486125440 # 0x41727101980
#         
# def connect_to_tracker(self, host, port)

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
#     host = 'udp://xbtt.sourceforge.net'
#     port = 2710
    
    while(1):       
        connection_id_send_dec = 4497486125440 # 0x41727101980 in dec as 64 bit integer (random?)
    
        action_send = 0 # 0 for connect 32 bit integer
        transaction_id_send = random.getrandbits(31) # random 32 bit int          
        connection_packet = make_connection_packet(connection_id_send_dec, action_send, transaction_id_send)
        
        response, address = send_packet_to_tracker(sock, host, port, connection_packet)
        print "******************************************"
        print "Binary response: " + str(response)
        
        
        # so now I've got a binary response
        connect_response_struct = struct.Struct('>iiq')
        action_recv, transaction_id_recv, connection_id_recv = connect_response_struct.unpack(response)
        print "Decimal response: " + str((action_recv, transaction_id_recv, connection_id_recv))
        print "******************************************"
        new_connection_id = check_packet(action_send, transaction_id_send, action_recv, transaction_id_recv, connection_id_recv)
    

def make_connection_packet(connection_id, action, transaction_id):
    
    connect_request_struct = struct.Struct('>qii')
    connection_packet_bin = connect_request_struct.pack(connection_id, action, transaction_id) # > for big endian, q for 64 bit int, i for 32 bit int
             
    connection_packet_hex = binascii.hexlify(connection_packet_bin)
    print "connection packet: " + str(connection_packet_hex)
    
    return connection_packet_bin

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

def check_packet(action_send, transaction_id_send, action_recv, transaction_id_recv, connection_id_recv):
    if action_recv != action_send:
        print "Action error!"
    elif transaction_id_send != transaction_id_recv:
        print 'Transaction id mismatch!'  
    else:
        print 'Exchange successful!'
    return connection_id_recv
            

if __name__ == '__main__':
    main()