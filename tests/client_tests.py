import binascii
import struct
import unittest

import client

class ClientTests(unittest.TestCase):
    
    def setUp(self):
        self.client = client.Client()
        self.connection_packet = self.client.make_connection_packet()
    
    def test_it_makes_a_16_byte_connection_packet(self):
        self.assertEqual(len(self.connection_packet), 16)
    
    def test_connection_packet_has_correct_connection_id(self):
        hex_packet = binascii.hexlify(self.connection_packet)
        self.assertEqual(hex_packet[:16], '0000041727101980')
    
    def test_connection_packet_has_correct_action(self):
        hex_packet = binascii.hexlify(self.connection_packet)
        self.assertEqual(hex_packet[16:24], '00000000')
    
    def test_connection_packet_has_correct_transaction_id(self):
        hex_packet = binascii.hexlify(self.connection_packet)
        bin_transaction_id = struct.Struct('>i').pack(self.client.current_transaction_id)
        hex_transaction_id = binascii.hexlify(bin_transaction_id)
        self.assertEqual(hex_packet[24:], hex_transaction_id)
    
    def test_it_opens_a_socket(self):
        sock = self.client.open_nonblocking_socket()
        self.assertGreater(sock, 0)
        
#     def test_announce_packet_contains_current_connection_id(self):
#         
#     def make_announce_packet(self):
# '''   
# size	        name	        description
# int64_t	        connection_id	The connection id acquired from establishing the connection.
# int32_t	        action	        Action. in this case, 1 for announce. See actions.
# int32_t	        transaction_id	Randomized by client.
# int8_t[20]	    info_hash	    The info-hash of the torrent you want announce yourself in.
# int8_t[20]	    peer_id	        Your peer id.
# int64_t	        downloaded	    The number of byte you've downloaded in this session.
# int64_t	        left	        The number of bytes you have left to download until you're finished.
# int64_t	        uploaded	    The number of bytes you have uploaded in this session.
# int32_t	        event           The event, one of:
#                                     none = 0
#                                     completed = 1
#                                     started = 2
#                                     stopped = 3
#                         
# uint32_t	    ip	            Your ip address. Set to 0 if you want the tracker to use the sender of this udp packet.
# uint32_t	    key	            A unique key that is randomized by the client.
# int32_t	        num_want	    The maximum number of peers you want in the reply. Use -1 for default.
# uint16_t	    port	        The port you're listening on.
# uint16_t	    extensions	    See extensions
# ''' 
        
    
    # to test:
    # send_packet_to_tracker(self, sock, host, port, packet)
    

if __name__ == '__main__':
    unittest.main()
