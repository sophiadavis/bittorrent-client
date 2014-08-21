'''
    UDP socket client
    protocol: http://www.rasterbar.com/products/libtorrent/udp_tracker_protocol.html
'''
import binascii
import bitstring
from collections import defaultdict
import hashlib
import os
import random
import socket
import struct  
import sys
import time
import urllib

from metainfo import *
import peer_connection

class Client(object):
    def __init__(self):
        self.connection_id = int('41727101980', 16)
        self.current_transaction_id = generate_random_32_bit_int()
        self.peer_id = os.urandom(20) # random 20-byte string
        self.key = generate_random_32_bit_int()
        self.active_peer_pool = defaultdict(list)
        
    def backoff(send_function):
        def backed_off(*args, **kwargs):
            for n in range(8):
                try:
                    print 'Packet sent.'
                    response = send_function(*args, **kwargs)
                    return response
            
                except socket.error as e:
                    print 'Excepting...\n'
                    sock = args[1]
                    sock.settimeout(1) # n
#                     time.sleep(1)  # (15 * 2**n)
        return backed_off
            
    def open_socket_with_timeout(self, timeout, type = 'udp'):
        if type == 'tcp':
            type = socket.SOCK_STREAM
        else:
            type = socket.SOCK_DGRAM
        try:
            sock = socket.socket(socket.AF_INET, type)
            sock.settimeout(timeout)
            return sock
        
        except socket.error:
            print 'Could not create socket'
            sys.exit() 
        
    
    def make_connection_packet(self):
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
            if action_recd == 0:
                print 'Connect packet received -- Resetting connection id.\n'
                connection_id_recd = unpack_binary_string('>q', response[8:])[0]
                self.connection_id = connection_id_recd
                return 0
            elif action_recd == 1:
                print 'Announce packet received.\n'
                return 0
            elif action_recd == 3:
                parse_error_packet(response)
            else:
                print 'Action not implemented'
                return -1
    
    def make_announce_packet(self, total_file_length, bencoded_info_hash):  
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

        announce_packet = preamble + info_hash + self.peer_id + download_info
        return announce_packet
        
    def get_list_of_peers(self, response):
        num_bytes = len(response)
        if num_bytes < 20:
            print "Error in getting peers"
        else:            
            interval, num_leechers, num_peers = unpack_binary_string('>iii', response[8:20])
            peers = []
            for n in xrange(num_peers):
                peer_start_index = (20 + 6 * n)
                peer_end_index = peer_start_index + 6
                ip, port = unpack_binary_string('>IH', response[peer_start_index : peer_end_index])
                ip = socket.inet_ntoa(struct.pack(">I", ip))
                print (ip, port)
                peers.append((ip, port))
            print "Returning list of %i peers (ip, port).\n" % num_peers
            return peers
            
        
        
    def parse_error_packet(response):
        pass
        # 32 -- action = 3
        # 32 -- transaction id
        # 8 -- error string
    
        
    def send_handshake(self, peer, bencoded_info_hash, num_pieces):
        ip = peer[0]
        port = peer[1]
        
        sock = self.open_socket_with_timeout(1, type = 'tcp')
    
        info_hash = hashlib.sha1(bencoded_info_hash).digest()
        handshake = self._make_handshake(info_hash)
        try:
            sock.connect((ip, port))
            sock.send(handshake)
            response_handshake, address = sock.recvfrom(1024)
            peer_id = self._verify_response_handshake(response_handshake, info_hash)
            if peer_id:
                peer = peer_connection.PeerConnection(ip, port, peer_id, sock, num_pieces)
                self._check_for_bitfield_message(peer)
                return peer
            else:
                print "Return handshake error"
        except socket.error:
            print "Socket connection error"
            return False
        
    
    def _make_handshake(self, info_hash):
        '''<pstrlen><pstr><reserved><info_hash><peer_id>'''
        pstr = 'BitTorrent protocol'
        pstrlen = pack_binary_string('>B', len(pstr))
        reserved = pack_binary_string('>8B', 0, 0, 0, 0, 0, 0, 0, 0)
        handshake_packet = pstrlen + pstr + reserved + info_hash + self.peer_id
        return handshake_packet
    
    def _verify_response_handshake(self, response_handshake, info_hash):
        if len(response_handshake) < 68:
            return False
        pstrlen_recd = unpack_binary_string('>B', response_handshake[0])[0]
        pstr_recd = response_handshake[1 : 20]
        reserved_recd = unpack_binary_string('>8B', response_handshake[20 : 28])
        info_hash_recd = response_handshake[28 : 48]
        peer_id_recd = response_handshake[48 : ]
        
        if pstrlen_recd != 19:
            return False
        if pstr_recd != 'BitTorrent protocol':
            return False
        if info_hash_recd != info_hash:
            return False
        # check for peer id??
        return peer_id_recd
    
    def send_interested(self):
        print "in send_interested\n"
        while self.active_peer_pool['choking']:
            peer = self.active_peer_pool['choking'].pop(0)
            print peer
            interested_message = pack_binary_string('>IB', 1, 2)

            try:
                peer.sock.send(interested_message)
                response, address = peer.sock.recvfrom(1024)
                if response:
                    print "* response! length: " + str(len(response))
                    print type(response)
                    length_and_id = response[:5]
                    length, id = unpack_binary_string('>IB', length_and_id)
                    print (length, id )
                    message_type = peer.parse_and_update_status_from_message(response, length, id)
                    if message_type == "unchoked":
                        self.active_peer_pool['unchoked'].append(peer)
            except socket.error:
                self.active_peer_pool['choking'].append(peer)
                continue
                
    def _check_for_bitfield_message(self, peer):
        response, address = peer.sock.recvfrom(1024)
        if response:
            print "got immediate response"
            print repr(response)
            print len(response)

#                     from pudb import set_trace; set_trace()
            length_and_id = response[:5]
            length, id = unpack_binary_string('>IB', length_and_id)
            if id not in range(10): # it's a bunch of haves
                print "haves!"
                while response:
                    msg_start = response.find('\x00\x00\x00\x05\x04')
                    length_and_id = response[msg_start : msg_start + 5]
                    length, id = unpack_binary_string('>IB', length_and_id)
                    peer.parse_and_update_status_from_message(response[msg_start:], length, id)
                    
                    response = response[msg_start + 4 + length: ]
            else:
                peer.parse_and_update_status_from_message(response, length, id)
            
        
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
    
if __name__ == '__main__':
    main()