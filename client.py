'''
    UDP socket client
    protocol: http://www.rasterbar.com/products/libtorrent/udp_tracker_protocol.html
'''
import binascii
import hashlib
import os
import random
import socket
import struct  
import sys
import time
import urllib

from metainfo import *


class Client:
    def __init__(self):
        self.connection_id = int('41727101980', 16)
        self.current_transaction_id = generate_random_32_bit_int()
        self.peer_id = os.urandom(20) # random 20-byte string
        self.key = generate_random_32_bit_int()   
        
    def backoff(send_function):
        def backed_off(*args, **kwargs):
            for n in range(8):
                try:
                    print 'Packet sent.'
                    response = send_function(*args, **kwargs)
                    return response
            
                except socket.error as e:
                    print 'Excepting...'
                    sock = args[1]
                    sock.settimeout(1) # n
#                     time.sleep(1)  # (15 * 2**n)
        return backed_off
            
    def open_socket_with_timeout(self, timeout):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            return sock
        
        except socket.error:
            print 'Could not create socket'
            sys.exit() 
        
    
    def make_connection_packet(self):
        '''
        size	        name	        description
        int64_t	        connection_id	Must be initialized to 0x41727101980 in network byte order. This will identify the protocol.
        int32_t	        action	        0 for a connection request
        int32_t	        transaction_id	Randomized by client.
        '''
        action = 0
        connection_packet = pack_binary_string('>qii', self.connection_id, action, self.current_transaction_id) # > = big endian, q = 64 bit, i = 32 bit
        return connection_packet
    
    
    @backoff
    def send_packet(self, sock, host, port, packet):
        sock.sendto(packet, (host, port))
        response, address = sock.recvfrom(1024)
        if response:
            return response, address
    

    def check_packet(self, action_sent, response):
        ''' Checks that action and transaction id are correct, and hands off response to appropriate parsing function'''
        action_recd = unpack_binary_string('>i', response[:4])[0]

        if (action_recd != action_sent) and (action_recd != 3):
            print "Action error!"
            return -1
        
        transaction_id_recd = unpack_binary_string('>i', response[4:8])[0]    
        
        if self.current_transaction_id != transaction_id_recd:
            print 'Transaction id mismatch!' 
            return -1 
        else:
            print 'Exchange successful!'
            if action_recd == 0:
                print 'Connect packet -- Resetting connection id.'
                connection_id_recd = unpack_binary_string('>q', response[8:])[0]
                self.connection_id = connection_id_recd
                return 0
            elif action_recd == 1:
                print 'Announce packet -- Getting peers.'
                return 0
            elif action_recd == 3:
                parse_error_packet(response)
            else:
                print 'Action not implemented'
                return -1
    
    def make_announce_packet(self, total_file_length, bencoded_info_hash):
        '''   
        size	        name	        description
        int64_t	        connection_id	The connection id acquired from establishing the connection.
        int32_t	        action	        Action. in this case, 1 for announce. See actions.
        int32_t	        transaction_id	Randomized by client.
        int8_t[20]	    info_hash	    The info-hash of the torrent you want announce yourself in.
        int8_t[20]	    peer_id	        Your peer id. 
        int64_t	        downloaded	    The number of byte you've downloaded in this session.
        int64_t	        left	        The number of bytes you have left to download until you're finished.
        int64_t	        uploaded	    The number of bytes you have uploaded in this session.
        int32_t	        event           The event, one of:
                                            none = 0
                                            completed = 1
                                            started = 2
                                            stopped = 3
                        
        uint32_t	    ip	            Your ip address. Set to 0 if you want the tracker to use the sender of this udp packet.
        uint32_t	    key	            A unique key that is randomized by the client.
        int32_t	        num_want	    The maximum number of peers you want in the reply. Use -1 for default.
        uint16_t	    port	        The port you're listening on.
        '''     
        action = 1
        self.current_transaction_id = generate_random_32_bit_int()
        bytes_downloaded = 0
        bytes_left = total_file_length - bytes_downloaded
        bytes_uploaded = 0
        event = 0
        ip = 0
        num_want = -1
        info_hash = hashlib.sha1(bencoded_info_hash).digest()
        
        preamble = pack_binary_string('>qii',
                                self.connection_id, 
                                action,
                                self.current_transaction_id)
                        
        download_info = pack_binary_string('>qqqiiiih',                                        
                                bytes_downloaded,
                                bytes_left,
                                bytes_uploaded,
                                event,
                                ip,
                                self.key,
                                num_want,
                                6881)

        announce_packet = preamble + \
                            info_hash + \
                            self.peer_id + \
                            download_info
        return announce_packet
        
    def get_list_of_peers(self, response):
        '''
        size	name	description
        int32_t	    action	        The action this is a reply to. Should in this case be 1 for announce. If 3 (for error) see errors. See actions.
        int32_t	    transaction_id	Must match the transaction_id sent in the announce request.
        int32_t	    interval	    the number of seconds you should wait until reannouncing yourself.
        int32_t	    leechers	    The number of peers in the swarm that has not finished downloading.
        int32_t	    seeders	        The number of peers in the swarm that has finished downloading and are seeding.
    
    + info about an invariable number of peers:
        int32_t	    ip	            The ip of a peer in the swarm.
        uint16_t	port	        The peer's listen port.
        '''
        num_bytes = len(response)
        if num_bytes < 20:
            print "Error in getting peers"
        else:            
            interval, num_leechers, num_seeders = unpack_binary_string('>iii', response[8:20])
            print str((interval, num_leechers, num_seeders))
            peers = []
            for n in xrange(num_seeders):
                peer_start_index = (20 + 6 * n)
                peer_end_index = peer_start_index + 6
                ip, port = unpack_binary_string('>ih', response[peer_start_index : peer_end_index])
                peers.append((ip, port))
            return peers
            
        
        
    def parse_error_packet(response):
        pass
        # 32 -- action = 3
        # 32 -- transaction id
        # 8 -- error string

def generate_random_32_bit_int():
    return random.getrandbits(31)

def pack_binary_string(format, *args):
    try:
        s = struct.Struct(format)
        packet = s.pack(*args)
        return packet
    except ValueError as e: #??
        print e

def unpack_binary_string(format, packet):
    try:
        s = struct.Struct(format)
        packet = s.unpack(packet)
        return packet
    except ValueError as e: #??
        print e

def main():
    
    host = 'thomasballinger.com';
    port = 6969;
    
    file = '../../walden.torrent'
    client = Client()
    sock = client.open_nonblocking_socket()
    print 'Socket created.\n'
    
    while(1):           
        connection_packet = client.make_connection_packet()
        response, address = client.send_packet(sock, host, port, connection_packet)
        status = client.check_packet(0, response)
        if status < 0:
            print 'Deal with error'
        else:
            print 'Success!'
            announce_packet = client.make_announce_packet()
            response, address = client.send_packet(sock, host, port, announce_packet) 
            print "Response 2: ----------------------------"
            print response 
            print "----------------------------"
            print len(response)
            client.get_peers_from_response(response)
            break
                  
    sock.close()
    
if __name__ == '__main__':
    main()