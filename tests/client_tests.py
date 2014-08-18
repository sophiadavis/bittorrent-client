import binascii
import os
import random
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
        sock = self.client.open_socket_with_timeout(1)
        self.assertGreater(sock, 0)
    
    def test_announce_packet_length(self):
        packet = self.client.make_announce_packet(1, os.urandom(20))
        self.assertEqual(len(packet), 98)
    
    def test_client_resets_connection_id_after_response(self):
        new_connection_id = random.randint(0, 127)
        response = client.pack_binary_string('>iiq', 0, self.client.current_transaction_id, new_connection_id)
        status = self.client.check_packet(0, response)
        self.assertEqual(status, 0)
        self.assertEqual(self.client.connection_id, new_connection_id)
        
        
        
#     def # send_packet(self, sock, host, port, packet):
    

if __name__ == '__main__':
    unittest.main()
