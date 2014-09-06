'''
Contains Client class, creating and managing the connection to a BitTorrent tracker.
'''
import hashlib
import os
import random
import socket
import struct  
import sys
import time

import message

from metainfo import *
import peer_connection

class Client(object):
    ''' Manages connection and communication to BitTorrent tracker'''

    def __init__(self):
        self.connection_id = int('41727101980', 16)
        self.current_transaction_id = generate_random_32_bit_int()
        self.peer_id = os.urandom(20) # random 20-byte string
        self.key = generate_random_32_bit_int()
        
    def backoff(send_function):
        ''' Returns a function in which the original function (to send and receive data 
             over a socket) is executed up to 8 times, with one second in between each try. 
             As soon as a response is received, it is returned.'''
        def backed_off(*args, **kwargs):
            for n in range(8):
                try:
                    print 'Packet sent.'
                    response = send_function(*args, **kwargs)
                    return response
            
                except socket.error as e:
                    print 'Excepting...\n'
                    sock = args[1]
                    sock.settimeout(1)
        return backed_off

    @backoff
    def send_packet(self, sock, host, port, packet):
        ''' Sends packet to a given host and port. 
            Returns a response, if the exchange is successful.'''
        sock.sendto(packet, (host, port))
        response = sock.recv(1024)
        if response:
            return response
    
    def make_connection_packet(self):
        ''' Creates a UDP-protocol connection packet to send to tracker.'''
        action = 0
        connection_packet = message.pack_binary_string('>qii', self.connection_id, action, self.current_transaction_id)
        return connection_packet
    
    def check_packet(self, action_sent, response):
        ''' Checks that action and transaction id are correct. Calls appropriate 
            parsing function to handle response. '''
        action_recd = message.unpack_binary_string('>i', response[:4])[0]

        if (action_recd != action_sent):
            print "Action error!"
            return -1
        
        transaction_id_recd = message.unpack_binary_string('>i', response[4:8])[0]    
        
        if self.current_transaction_id != transaction_id_recd:
            print 'Transaction id mismatch!' 
            return -1 
        else:
            if action_recd == 0:
                print 'Connect packet received -- Resetting connection id.\n'
                connection_id_recd = message.unpack_binary_string('>q', response[8:])[0]
                self.connection_id = connection_id_recd
                return 0
            elif action_recd == 1:
                print 'Announce packet received.\n'
                return 0
            else:
                print 'Action not implemented'
                return -1
    
    def make_announce_packet(self, total_file_length, bencoded_info_hash): 
        ''' Creates a UDP-protocol announce packet to send to tracker.''' 
        action = 1
        self.current_transaction_id = generate_random_32_bit_int()
        bytes_downloaded = 0
        bytes_left = total_file_length - bytes_downloaded
        bytes_uploaded = 0
        event = 0
        ip = 0
        num_want = -1
        info_hash = hashlib.sha1(bencoded_info_hash).digest()
        
        preamble = message.pack_binary_string('>qii',
                                              self.connection_id, 
                                              action,
                                              self.current_transaction_id)
                        
        download_info = message.pack_binary_string('>qqqiiiih',                                        
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
        ''' Parses tracker's response to announce packet, returning list of peers 
            in (ip, port) format. ''' 
        num_bytes = len(response)
        if num_bytes < 20:
            print "Error in getting peers"
        else:            
            interval, num_leechers, num_peers = message.unpack_binary_string('>iii', response[8:20])
            peers = []
            for n in xrange(num_peers):
                peer_start_index = (20 + 6 * n)
                peer_end_index = peer_start_index + 6
                ip, port = message.unpack_binary_string('>IH', response[peer_start_index : peer_end_index])
                ip = socket.inet_ntoa(struct.pack(">I", ip))
                print (ip, port)
                peers.append((ip, port))
            print "Returning list of %i peers (format: (ip, port)).\n" % num_peers
            return peers
    
    def build_peer(self, (ip, port), num_pieces, info_hash, torrent_download):
        ''' Creates a peer object for coordinating communication with a peer. ''' 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(0)
        peer = peer_connection.PeerConnection(ip, port, sock, num_pieces, info_hash, torrent_download)
        return peer
        
def open_socket_with_timeout(timeout, type = 'udp'):
    ''' Creates a tcp or udp socket (if timeout == 0, socket is nonblocking. '''
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
        
def generate_random_32_bit_int():
    return random.getrandbits(31)
