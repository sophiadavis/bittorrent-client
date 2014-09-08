from collections import OrderedDict
import unittest

import bencoder
import metainfo

class BencoderTests(unittest.TestCase):
    
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
        decoded_int = bencoder._decode_next_int(self.b_int)[0]
        self.assertEqual(decoded_int, 3)
    
    def test_it_decodes_negatives(self):
        decoded_int = bencoder._decode_next_int(self.b_neg_int)[0]
        self.assertEqual(decoded_int, -3)
        
    def test_it_decodes_strings(self):
        decoded_str = bencoder._decode_next_string(self.b_str)[0]
        self.assertEqual(decoded_str, 'publisher-webpage')

############################    
# test encoding of units (ints and strings)
    def test_it_encodes_ints(self):
        bencoded_int = bencoder._encode_int(3)
        self.assertEqual(bencoded_int, self.b_int)
        
    def test_it_encodes_strings(self):
        bencoded_str = bencoder._encode_string('publisher-webpage')
        self.assertEqual(bencoded_str, self.b_str)
        
############################            
# test decoding of lists    
    def test_it_decodes_lists(self):
        decoded_list = bencoder.decode(self.b_list)[0]
        self.assertEqual(decoded_list, ['spam', 'eggs'])
    
    def test_it_decodes_single_item_lists(self):
        decoded_list = bencoder.decode(self.b_single_word_list)[0]
        self.assertEqual(decoded_list, ['Distributed by Mininova.txt'])
    
    def test_it_decodes_nested_lists(self):
        decoded_list = bencoder.decode(self.b_nested_list)[0]
        self.assertEqual(decoded_list, [['spam', 'eggs'], ['spam', 'eggs']]) 

############################            
# test encoding of lists 
    def test_it_encodes_lists(self):
        encoded_list = bencoder.encode(['spam', 'eggs'])
        self.assertEqual(encoded_list, self.b_list)

    def test_it_encodes_single_item_lists(self):
        encoded_list = bencoder.encode(['Distributed by Mininova.txt'])
        self.assertEqual(encoded_list, self.b_single_word_list)
    
    def test_it_encodes_nested_lists(self):
        encoded_list = bencoder.encode([['spam', 'eggs'], ['spam', 'eggs']])
        self.assertEqual(encoded_list, self.b_nested_list)

############################    
# test decoding of dicts
    def test_it_decodes_a_dict_of_strings(self):
        decoded_dict = bencoder.decode(self.little_b_dict)[0]
        self.assertEqual(decoded_dict.keys(), ['cow', 'spam'])
        self.assertEqual(decoded_dict.values(), ['moo', 'eggs']) 
        
    def test_it_decodes_a_bigger_dict(self):
        decoded_dict = bencoder.decode(self.bigger_b_dict)[0]
        self.assertEqual(decoded_dict.keys(), ['publisher', 'publisher-webpage', 'publisher.location'])
        self.assertEqual(decoded_dict.values(), ['bob', 'www.example.com', 'home'])
            
    def test_it_decodes_a_dict_with_list_values(self):
        decoded_dict = bencoder.decode(self.dict_w_lists)[0]
        self.assertEqual(decoded_dict.keys(), ['spam', 'eggs'])
        self.assertEqual(decoded_dict.values(), [['a', 'b'], ['a', 'b']])
     
    def test_it_decodes_dicts_w_some_numbers(self):
        decoded_dict = bencoder.decode(self.dict_w_nums)[0]
        self.assertEqual(decoded_dict.keys(), ['bar', 'foo'])
        self.assertEqual(decoded_dict.values(), ['spam', 42])  
        
    def test_it_decodes_dicts_w_nums_and_lists(self):
        decoded_dict = bencoder.decode(self.dict_w_nums_and_lists)[0]
        self.assertEqual(decoded_dict.keys(), ['length', 'path'])
        self.assertEqual(decoded_dict.values(), [291, ['Distributed by Mininova.txt']])       
    
    def test_it_decodes_actual_bittorrent_files(self):
        decoded_dict = bencoder.decode(self.metainfo_file)[0]
        self.assertTrue(decoded_dict.keys())

############################ 
# test encoding of dicts
    def test_it_decodes_a_dict_of_strings(self):
        encoded_dict = bencoder.encode(OrderedDict([('cow', 'moo'), ('spam', 'eggs')]))
        self.assertEqual(encoded_dict, self.little_b_dict)
        
    def test_it_encodes_a_bigger_dict(self):
        encoded_dict = bencoder.encode(OrderedDict([('publisher', 'bob'), ('publisher-webpage', 'www.example.com'), ('publisher.location', 'home')]))
        self.assertEqual(encoded_dict, self.bigger_b_dict)
    
    def test_it_encodes_a_dict_with_list_values(self):
        encoded_dict = bencoder.encode(OrderedDict([('spam', ['a', 'b']), ('eggs', ['a', 'b'])]))
        self.assertEqual(encoded_dict, self.dict_w_lists)

    def test_it_encodes_dicts_w_some_numbers(self):
        encoded_dict = bencoder.encode(OrderedDict([('bar', 'spam'), ('foo', 42)]))
        self.assertEqual(encoded_dict, self.dict_w_nums)
        
    def test_it_encodes_dicts_w_nums_and_lists(self):
        encoded_dict = bencoder.encode(OrderedDict([('length', 291), ('path', ['Distributed by Mininova.txt'])]))
        self.assertEqual(encoded_dict, self.dict_w_nums_and_lists)
        
    def test_it_encodes_actual_bittorrent_files(self):
        decoded_dict = bencoder.decode(self.metainfo_file)[0]
        encoded_file = bencoder.encode(decoded_dict)
        self.assertEqual(self.metainfo_file, encoded_file)
        
############################ 
# test that encoding a decoded metainfo file works 'round trip'
    def test_reversing_comic(self):
        t = metainfo.MetainfoFile(self.comics)
        encoded_torrent = bencoder.encode(t._parsed_text)
        self.assertEqual(t._bencoded_text, encoded_torrent)
    
    def test_reversing_walden(self):
        t = metainfo.MetainfoFile(self.walden)
        encoded_torrent = bencoder.encode(t._parsed_text)
        self.assertEqual(t._bencoded_text, encoded_torrent)