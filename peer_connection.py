import bitstring
import hashlib
import socket

import client
import message
import session
import torrent

MESSAGE_TYPE_DICT = {   'choke' : 0,
                        'unchoke' : 1,
                        'interested' : 2,
                        'not-interested' : 3,
                        'have' : 4,
                        'bitfield' : 5,
                        'request' : 6,
                        'piece' : 7,
                        'cancel' : 8,
                        'port' : 9    }

class PeerConnection(object):
    
    def __init__(self, ip, port, sock, num_pieces, info_hash, shared_torrent_status_tracker):
        self.ip = ip
        self.port = port
        self.sock = sock
        self.status = 'choked'
        self.last_message_scheduled = None
        self.in_buffer = ''
        self.out_buffer = ''
        self.pieces = [0] * num_pieces
        self.info_hash_digest = hashlib.sha1(info_hash).digest()
        self.shared_torrent_status_tracker = shared_torrent_status_tracker
        
    def fileno(self):
        return self.sock.fileno()
        
    def __str__(self):
        return '%s:%i -- status: %s' % (str(self.ip), self.port, self.status)
    
    def _parse_choke(self, packet, length):
        self.status = 'choked'
        print 'choke'
        return "choke"
    
    def _parse_and_respond_to_unchoke(self, packet, length):
        self.status = 'unchoked'
        print 'unchoked'
        self._schedule_request()
        return 'unchoked'
    
    def _parse_bitfield(self, packet, length):
        print "bitfield"
        print repr(packet)
        bitstr = bitstring.BitArray(bytes = packet[5 : length + 4])
        
        from pudb import set_trace; set_trace()
        for i, have_bit in enumerate(bitstr):
            try:
                self.pieces[i] = 1 if have_bit else 0
            except IndexError:
                if have_bit:
                    return False # Spare bits are set
                else:
                    pass
        if i > len(self.pieces) + 8: # Make sure bitfield is correct size
            return False
            
        return True
    
    def _parse_have(self, packet, length):
        piece_num = message.unpack_binary_string('>I', packet[5 : length + 4])[0]
        print "HAVE" + str(piece_num)
        self.pieces[piece_num] = 1
        return True
        
    def parse_and_update_status_from_message(self, packet, length, id):
        print "PARSING"
#         print (length, id)
        MESSAGE_PARSE_DICT = {  0 : self._parse_choke,
                                1 : self._parse_and_respond_to_unchoke,
            #                    2 : self._parse_and_respond_to_interested,
            #                         3 : self._parse_uninterested,            
                                4 : self._parse_have,
                                5 : self._parse_bitfield,
            #                         6 : parse_request,
                                7 : self._parse_piece }#,
            #                         8 : parse_cancel,
            #                         9 : parse_port  }
    
    
#         from pudb import set_trace; set_trace()
        if int(id) in range(9):
            status = MESSAGE_PARSE_DICT[id](packet, length)
                pass
                # DROP CONNECTION
            return True
        else:
            print "Message not recognized"

        
    def schedule_handshake(self, client_peer_id):
        handshake = self._make_handshake(client_peer_id)
        self.out_buffer += handshake
        self.last_message_scheduled = 'handshake'
        
    
    def _make_handshake(self, client_peer_id):
        '''<pstrlen><pstr><reserved><info_hash><peer_id>'''
        pstr = 'BitTorrent protocol'
        pstrlen = message.pack_binary_string('>B', len(pstr))
        reserved = message.pack_binary_string('>8B', 0, 0, 0, 0, 0, 0, 0, 0)
        handshake_packet = pstrlen + pstr + reserved + self.info_hash_digest + client_peer_id
        return handshake_packet
    
    def verify_response_handshake(self, response_handshake):
        if len(response_handshake) < 68:
            return False
        pstrlen_recd = message.unpack_binary_string('>B', response_handshake[0])[0]
        pstr_recd = response_handshake[1 : 20]
        reserved_recd = message.unpack_binary_string('>8B', response_handshake[20 : 28])
        info_hash_recd = response_handshake[28 : 48]
        
        if pstrlen_recd != 19:
            return False
        if pstr_recd != 'BitTorrent protocol':
            return False
        if info_hash_recd != self.info_hash_digest:
            print repr(info_hash_recd)
            print repr(self.info_hash_digest)
            return False
        return True
    
    def _schedule_interested(self):
        interested_message = message.pack_binary_string('>IB', 1, 2)
        self.out_buffer += interested_message
    
    def handle_in_buffer(self):
        print "**** handle in buffer"
        print repr(self.in_buffer)
        print len(self.in_buffer)
        
        if len(self.in_buffer) <= 3:
            return False
            
        if self.verify_response_handshake(self.in_buffer):
            self.in_buffer = self.in_buffer[68:]
            print "Handshake verified"
            self._schedule_interested()
            self.last_message_scheduled = "Interested"
            return True
        
        length = int(message.unpack_binary_string(">I", self.in_buffer[:4])[0])
        if len(self.in_buffer) < int(length) + 4:
            return False # Complete message has not yet arrived
        
        # Keep alive message has length 0 -- no id
        if length == 0:
            self.in_buffer = self.in_buffer[4:]
            return True
        
        # All other messages have an id
        id = int(message.unpack_binary_string('>B', self.in_buffer[4])[0])
        
        self.parse_and_update_status_from_message(self.in_buffer[:length + 4], length, id)
        self.in_buffer = self.in_buffer[length + 4:]
        return True
    
    def send_from_out_buffer(self):
        try:
            sent = self.sock.send(self.out_buffer)
            self.out_buffer = self.out_buffer[sent:]
            return True
        except socket.error as e:
            print e
            return False
        
        
  
  
  
  
  
  