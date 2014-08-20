import bencoder
from collections import OrderedDict
import os
import unittest

import metainfo

class MetainfoTests(unittest.TestCase):
    
    def setUp(self):
        self.comics = '../../Wer ist wer bei Conny Van Ehlsing ... Gaijin PDF [mininova].torrent'
        self.walden = '../../walden.torrent'

############################   
# test MetainfoFile class     
    def test_it_decodes_from_file_comic(self):
        t = metainfo.MetainfoFile(self.comics)
        self.assertTrue(t._parsed_text.keys())
    
    def test_torrent_prints_comic(self):
        t = metainfo.MetainfoFile(self.comics)
        self.assertIsNotNone(t.__str__())
    
    # dumb
    def test_it_decodes_from_file_walden(self):
        t = metainfo.MetainfoFile(self.walden)
        self.assertTrue(t._parsed_text.keys())
    
    def test_torrent_prints_walden(self):
        t = metainfo.MetainfoFile(self.walden)
        self.assertIsNotNone(t.__str__())
    
    # dumb test
    def test_it_can_return_info_hash(self):
        t = metainfo.MetainfoFile(self.comics)
        self.assertIsNotNone(t.bencoded_info_hash)
    
    # dumb test
    def test_it_calculates_total_length(self):
        t = metainfo.MetainfoFile(self.walden)
        self.assertGreater(t.total_length, 0) # test on single file torrent 
    
    def test_it_has_tracker_url_and_port(self):
        t = metainfo.MetainfoFile(self.walden)
        self.assertEqual(t.announce_url_and_port, ('tracker.publicbt.com', 80))
    
    def test_it_gets_num_pieces(self):
        t = metainfo.MetainfoFile(self.walden)
        print t.num_pieces
#         self.assertEqual(t.num_pieces, ('tracker.publicbt.com', 80))
    

if __name__ == '__main__':
    unittest.main()
