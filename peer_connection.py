'''
Contains PeerConnection class to facilitate message passing with each peer.
'''
import bitstring
import hashlib
import socket

import client
import message
import session
import torrent

'''BitTorrent protocol IDs for peer-to-peer messages. '''
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
    ''' Manages message passing with a given peer. '''

    def __init__(self, ip, port, sock, num_pieces, info_hash, torrent_download):
        self.ip = ip
        self.port = port
        self.sock = sock
        self.status = 'unverified'
        self.last_message_scheduled = None
        self.in_buffer = ''
        self.out_buffer = ''
        self.pieces = [0] * (num_pieces)
        self.info_hash_digest = hashlib.sha1(info_hash).digest()
        self.torrent_download = torrent_download
        self.num_outstanding_requests = 0

    def fileno(self):
        ''' Define a fileno so select can function directly with PeerConnection object. '''
        return self.sock.fileno()

    def __str__(self):
        return '%s:%i -- status: %s, num requests: %i, last scheduled: %s' % (str(self.ip), self.port, self.status, self.num_outstanding_requests, self.last_message_scheduled)

    '''
    Methods for parsing incoming peer-to-peer messages.
    PeerConnection and Torrent object are updated accordingly.
    '''
    def _verify_response_handshake(self, response_handshake):
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
            return False
        return True

    def _parse_choke(self, packet, length):
        self.status = 'choked'
        print '++++++++++++++++++++ choke'
        return True

    def _parse_and_respond_to_unchoke(self, packet, length):
        self.status = 'unchoked'
        print '++++++++++++++++++++ unchoke'
        status = self._schedule_request()
        if status == "DONE":
            return "DONE"
        return True

    def _parse_bitfield(self, packet, length):
        bitstr = bitstring.BitArray(bytes = packet[5 : length + 4])
        print "++++++++++++++++++++ bitfield (length: %i): " % len(bitstr)

        for i, have_bit in enumerate(bitstr):
            try:
                self.pieces[i] = 1 if have_bit else 0
            except IndexError:
                if have_bit:
                    print "Spare bits set in bitfield."
                    return False
                else:
                    pass
        if i > len(self.pieces) + 8:
            print "Incorrect sized bitfield."
            return False

        return True

    def _parse_have(self, packet, length):
        piece_num = message.unpack_binary_string('>I', packet[5 : length + 4])[0]
        print "++++++++++++++++++++ have: " + str(piece_num)
        try:
            self.pieces[piece_num] = 1
        except IndexError:
            print "Piece index out of range"
        return True

    def _parse_piece(self, packet, length):
        index, begin = message.unpack_binary_string('>II', packet[5 : 13])
        block = packet[13 : length + 4]
        print "++++++++++++++++++++ piece (length: %i, piece: %i, begin: %i)" % (len(block), index, begin)

        self.torrent_download.process_piece(index, begin, block)
        self.num_outstanding_requests -= 1
        status = self._schedule_request()
        self.last_message_scheduled = "request"
        return True

    def parse_and_update_status_from_message(self, packet, length, msg_id):
        MESSAGE_ID_DICT = {  0 : self._parse_choke,
                                1 : self._parse_and_respond_to_unchoke,
                                4 : self._parse_have,
                                5 : self._parse_bitfield,
                                7 : self._parse_piece }

        if int(msg_id) in MESSAGE_ID_DICT:
            return MESSAGE_ID_DICT[msg_id](packet, length)
        else:
            print "++++++++++++++++++++ Message not implemented."


    '''
    Methods for forming and scheduling outgoing peer-to-peer messages, according to the
        current status of the download (Torrent object).
    PeerConnection is updated accordingly.
    '''
    def schedule_handshake(self, client_peer_id):
        handshake = self._make_handshake(client_peer_id)
        self.out_buffer += handshake
        self.last_message_scheduled = 'handshake'

    def _make_handshake(self, client_peer_id):
        pstr = 'BitTorrent protocol'
        pstrlen = message.pack_binary_string('>B', len(pstr))
        reserved = message.pack_binary_string('>8B', 0, 0, 0, 0, 0, 0, 0, 0)
        handshake_packet = pstrlen + pstr + reserved + self.info_hash_digest + client_peer_id
        return handshake_packet

    def _schedule_interested(self):
        print "....... scheduled interested"
        interested_message = message.pack_binary_string('>IB', 1, 2)
        self.out_buffer += interested_message

    def _schedule_request(self):
        if self.num_outstanding_requests < 1:
            peer_has_piece = False
            while not peer_has_piece:
                next = self.torrent_download.strategically_get_next_request()
                if next == "DONE":
                    return "DONE"
                index, begin, length = next
                peer_has_piece = self.pieces[index]

            request_message = message.pack_binary_string('>IBIII', 13, 6, index, begin, length)
            print "....... scheduled request for piece %i, byte-offset %i (%i bytes)" % (index, begin, length)
            self.out_buffer += request_message
            self.num_outstanding_requests += 1

    def handle_in_buffer(self):
        ''' Process first complete message (if one exists) in PeerConnection's incoming
                message buffer. Remove bytes in this message from in-buffer.
            Returns True if a complete message has been parsed, DONE if download is complete,
                and False if buffer did not contain a complete message.'''

        print "**** handle in buffer, length: %i\n" % len(self.in_buffer)

        if len(self.in_buffer) <= 3:
            return False

        if self._verify_response_handshake(self.in_buffer):
            self.in_buffer = self.in_buffer[68:]
            print "Handshake verified"
            self.status = 'choked'
            self._schedule_interested()
            self.last_message_scheduled = "interested"
            return True

        if self.status == 'choked':
            self._schedule_interested()
            self.last_message_scheduled = "interested"

        if self.status == 'unchoked':
            status = self._schedule_request()
            self.last_message_scheduled = "request"
            if status == "DONE":
                return "DONE"

        length = int(message.unpack_binary_string(">I", self.in_buffer[:4])[0])
        if len(self.in_buffer) < int(length) + 4:
            return False # Complete message has not yet arrived

        # Keep alive message has length 0 -- and no id
        if length == 0:
            self.in_buffer = self.in_buffer[4:]
            return True

        msg_id = int(message.unpack_binary_string('>B', self.in_buffer[4])[0])

        status = self.parse_and_update_status_from_message(self.in_buffer[:length + 4], length, msg_id)
        if status == "DONE":
            return "DONE"

        self.in_buffer = self.in_buffer[length + 4:]
        return True

    def send_from_out_buffer(self):
        ''' Sends from PeerConnection's buffer of scheduled messages, if possible.
            Any successfully sent bytes are removed from buffer.'''

        print "**** processing out buffer, length: %(length)i\n" % {"length" : len(self.out_buffer)}
        try:
            sent = self.sock.send(self.out_buffer)
            self.out_buffer = self.out_buffer[sent:]
            print "Sent %i bytes" % sent
        except socket.error as e:
            print "Sent 0 bytes (" + repr(e) + ")"

    def receive_to_in_buffer(self):
        ''' Receive to the in buffer of the peer and dispatch to handle_in_buffer'''
        try:
            response = peer.sock.recv(1024)
            if not response:
                return False
        except socket.error as e:
            print e
            return True # what should we actually do here?

        self.in_buffer += response
        status = self.handle_in_buffer()
        while status is True:
            status = self.handle_in_buffer()
        return status
