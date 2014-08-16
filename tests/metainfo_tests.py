from collections import OrderedDict
import os
import unittest

import metainfo

class MetainfoTests(unittest.TestCase):
    
    def setUp(self):
        self.b_list = 'l4:spam4:eggse'
        self.b_str = '17:publisher-webpage'
        self.b_single_word_list = 'l27:Distributed by Mininova.txte'
        self.b_nested_list = 'll4:spam4:eggsel4:spam4:eggsee'
        self.b_int = 'i3e'
        self.b_neg_int = 'i-3e'
        self.little_b_dict = 'd3:cow3:moo4:spam4:eggse'
        self.bigger_b_dict = 'd9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:homee'
        self.dict_w_lists = 'd4:spaml1:a1:be4:eggsl1:a1:bee'
        self.dict_w_nums = 'd3:bar4:spam3:fooi42ee'
        self.dict_w_nums_and_lists = 'd6:lengthi291e4:pathl27:Distributed by Mininova.txtee'
        self.metainfo_file = 'd8:announce36:http://tracker.mininova.org/announce7:comment41:Auto-generated torrent by Mininova.org CD13:creation datei1338819405e4:infod5:filesld6:lengthi291e4:pathl27:Distributed by Mininova.txteed6:lengthi116e4:pathl12:Homepage.urleed6:lengthi272e4:pathl10:Lizenz.txteed6:lengthi2739439e4:pathl55:Vaehling-wer ist wer bei Conny Van Ehlsing - Gaijin.pdfeed6:lengthi29109e4:pathl15:dreadfulgate[1]eee4:name48:Wer ist wer bei Conny Van Ehlsing ... Gaijin PDF12:piece lengthi1048576eee'
        self.comics = '../../Wer ist wer bei Conny Van Ehlsing ... Gaijin PDF [mininova].torrent'
        self.walden = '../../walden.torrent'

############################    
# test decoding of units (ints and strings)
    def test_it_decodes_ints(self):
        decoded_int = metainfo.decode_next_int(self.b_int)[0]
        self.assertEqual(decoded_int, 3)
    
    def test_it_decodes_negatives(self):
        decoded_int = metainfo.decode_next_int(self.b_neg_int)[0]
        self.assertEqual(decoded_int, -3)
        
    def test_it_decodes_strings(self):
        decoded_str = metainfo.decode_next_string(self.b_str)[0]
        self.assertEqual(decoded_str, 'publisher-webpage')

############################    
# test encoding of units (ints and strings)
    def test_it_encodes_ints(self):
        bencoded_int = metainfo.encode_int(3)
        self.assertEqual(bencoded_int, self.b_int)
        
    def test_it_encodes_strings(self):
        bencoded_str = metainfo.encode_string('publisher-webpage')
        self.assertEqual(bencoded_str, self.b_str)
        
############################            
# test decoding of lists    
    def test_it_decodes_lists(self):
        decoded_list = metainfo.decode(self.b_list)[0]
        self.assertEqual(decoded_list, ['spam', 'eggs'])
    
    def test_it_decodes_single_item_lists(self):
        decoded_list = metainfo.decode(self.b_single_word_list)[0]
        self.assertEqual(decoded_list, ['Distributed by Mininova.txt'])
    
    def test_it_decodes_nested_lists(self):
        decoded_list = metainfo.decode(self.b_nested_list)[0]
        self.assertEqual(decoded_list, [['spam', 'eggs'], ['spam', 'eggs']]) 

############################            
# test encoding of lists 
    def test_it_encodes_lists(self):
        encoded_list = metainfo.encode(['spam', 'eggs'])
        self.assertEqual(encoded_list, self.b_list)

    def test_it_encodes_single_item_lists(self):
        encoded_list = metainfo.encode(['Distributed by Mininova.txt'])
        self.assertEqual(encoded_list, self.b_single_word_list)
    
    def test_it_encodes_nested_lists(self):
        encoded_list = metainfo.encode([['spam', 'eggs'], ['spam', 'eggs']])
        self.assertEqual(encoded_list, self.b_nested_list)

############################    
# test decoding of dicts
    def test_it_decodes_a_dict_of_strings(self):
        decoded_dict = metainfo.decode(self.little_b_dict)[0]
        self.assertEqual(decoded_dict.keys(), ['cow', 'spam'])
        self.assertEqual(decoded_dict.values(), ['moo', 'eggs']) 
        
    def test_it_decodes_a_bigger_dict(self):
        decoded_dict = metainfo.decode(self.bigger_b_dict)[0]
        self.assertEqual(decoded_dict.keys(), ['publisher', 'publisher-webpage', 'publisher.location'])
        self.assertEqual(decoded_dict.values(), ['bob', 'www.example.com', 'home'])
            
    def test_it_decodes_a_dict_with_list_values(self):
        decoded_dict = metainfo.decode(self.dict_w_lists)[0]
        self.assertEqual(decoded_dict.keys(), ['spam', 'eggs'])
        self.assertEqual(decoded_dict.values(), [['a', 'b'], ['a', 'b']])
     
    def test_it_decodes_dicts_w_some_numbers(self):
        decoded_dict = metainfo.decode(self.dict_w_nums)[0]
        self.assertEqual(decoded_dict.keys(), ['bar', 'foo'])
        self.assertEqual(decoded_dict.values(), ['spam', 42])  
        
    def test_it_decodes_dicts_w_nums_and_lists(self):
        decoded_dict = metainfo.decode(self.dict_w_nums_and_lists)[0]
        self.assertEqual(decoded_dict.keys(), ['length', 'path'])
        self.assertEqual(decoded_dict.values(), [291, ['Distributed by Mininova.txt']])       
    
    def test_it_decodes_actual_bittorrent_files(self):
        decoded_dict = metainfo.decode(self.metainfo_file)[0]
        self.assertTrue(decoded_dict.keys())

############################ 
# test encoding of dicts
    def test_it_decodes_a_dict_of_strings(self):
        encoded_dict = metainfo.encode(OrderedDict([('cow', 'moo'), ('spam', 'eggs')]))
        self.assertEqual(encoded_dict, self.little_b_dict)
        
    def test_it_encodes_a_bigger_dict(self):
        encoded_dict = metainfo.encode(OrderedDict([('publisher', 'bob'), ('publisher-webpage', 'www.example.com'), ('publisher.location', 'home')]))
        self.assertEqual(encoded_dict, self.bigger_b_dict)
    
    def test_it_encodes_a_dict_with_list_values(self):
        encoded_dict = metainfo.encode(OrderedDict([('spam', ['a', 'b']), ('eggs', ['a', 'b'])]))
        self.assertEqual(encoded_dict, self.dict_w_lists)

    def test_it_encodes_dicts_w_some_numbers(self):
        encoded_dict = metainfo.encode(OrderedDict([('bar', 'spam'), ('foo', 42)]))
        self.assertEqual(encoded_dict, self.dict_w_nums)
        
    def test_it_encodes_dicts_w_nums_and_lists(self):
        encoded_dict = metainfo.encode(OrderedDict([('length', 291), ('path', ['Distributed by Mininova.txt'])]))
        self.assertEqual(encoded_dict, self.dict_w_nums_and_lists)
        
    def test_it_encodes_actual_bittorrent_files(self):
        decoded_dict = metainfo.decode(self.metainfo_file)[0]
        encoded_file = metainfo.encode(decoded_dict)
        self.assertEqual(self.metainfo_file, encoded_file)


############################   
# test MetainfoFile class     
    def test_it_decodes_from_file_comic(self):
        t = metainfo.MetainfoFile(self.comics)
        self.assertTrue(t.parsed_text.keys())
    
    def test_torrent_prints_comic(self):
        t = metainfo.MetainfoFile(self.comics)
        self.assertIsNotNone(t.__str__())
        
    def test_it_decodes_from_file_walden(self):
        t = metainfo.MetainfoFile(self.walden)
        self.assertTrue(t.parsed_text.keys())
    
    def test_torrent_prints_walden(self):
        t = metainfo.MetainfoFile(self.walden)
        self.assertIsNotNone(t.__str__())
    
    def test_reversing_comic(self):
        t = metainfo.MetainfoFile(self.comics)
        encoded_torrent = metainfo.encode(t.parsed_text)
        self.assertEqual(t.bencoded_text, encoded_torrent)
    
    def test_reversing_walden(self):
        t = metainfo.MetainfoFile(self.walden)
        encoded_torrent = metainfo.encode(t.parsed_text)
        self.assertEqual(t.bencoded_text, encoded_torrent)
    
    # dumb test
    def test_it_can_return_info_hash(self):
        t = metainfo.MetainfoFile(self.comics)
        self.assertIsNotNone(t.bencoded_info_hash)
    
    # dumb test
    def test_it_calculates_total_length(self):
        t = metainfo.MetainfoFile(self.walden)
        self.assertGreater(t.get_total_length(), 0) # test on single file torrent 
    
    def test_it_has_tracker_url_and_port(self):
        t = metainfo.MetainfoFile(self.walden)
        self.assertEqual(t.get_announce_url_and_port(), ('tracker.publicbt.com', 80))
    

if __name__ == '__main__':
    unittest.main()
