import unittest
import re

import myBencoder

class BencodeTests(unittest.TestCase):
    
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
        self.torrent = 'd8:announce36:http://tracker.mininova.org/announce7:comment41:Auto-generated torrent by Mininova.org CD13:creation datei1338819405e4:infod5:filesld6:lengthi291e4:pathl27:Distributed by Mininova.txteed6:lengthi116e4:pathl12:Homepage.urleed6:lengthi272e4:pathl10:Lizenz.txteed6:lengthi2739439e4:pathl55:Vaehling-wer ist wer bei Conny Van Ehlsing - Gaijin.pdfeed6:lengthi29109e4:pathl15:dreadfulgate[1]eee4:name48:Wer ist wer bei Conny Van Ehlsing ... Gaijin PDF12:piece lengthi1048576eee'
    
# test decoding of units (ints and strings)
    def test_it_decodes_ints(self):
        decoded_int, rest = myBencoder.decode_next_int(self.b_int)
        self.assertEqual(decoded_int, 3)
    
    def test_it_decodes_negatives(self):
        decoded_int, rest = myBencoder.decode_next_int(self.b_neg_int)
        self.assertEqual(decoded_int, -3)
        
    def test_it_decodes_strings(self):
        decoded_str, rest = myBencoder.decode_next_string(self.b_str)
        self.assertEqual(decoded_str, 'publisher-webpage')
    
# test decoding of lists    
    def test_it_decodes_lists(self):
        decoded_list, rest = myBencoder.decode(self.b_list)
        self.assertEqual(decoded_list, ['spam', 'eggs'])
    
    def test_it_decodes_single_item_lists(self):
        decoded_list, rest = myBencoder.decode(self.b_single_word_list)
        self.assertEqual(decoded_list, ['Distributed by Mininova.txt'])
    
    def test_it_decodes_nested_lists(self):
        decoded_list, rest = myBencoder.decode(self.b_nested_list)
        self.assertEqual(decoded_list, [['spam', 'eggs'], ['spam', 'eggs']]) 
    
# test decoding of lists
    def test_it_decodes_a_dict_of_strings(self):
        decoded_dict, rest = myBencoder.decode(self.little_b_dict)
        self.assertEqual(decoded_dict.keys(), ['cow', 'spam'])
        self.assertEqual(decoded_dict.values(), ['moo', 'eggs']) 
        
    def test_it_decodes_a_bigger_dict(self):
        decoded_dict, rest = myBencoder.decode(self.bigger_b_dict)
        self.assertEqual(decoded_dict.keys(), ['publisher', 'publisher-webpage', 'publisher.location'])
        self.assertEqual(decoded_dict.values(), ['bob', 'www.example.com', 'home'])
            
    def test_it_decodes_a_dict_with_list_values(self):
        decoded_dict, rest = myBencoder.decode(self.dict_w_lists)
        self.assertEqual(decoded_dict.keys(), ['spam', 'eggs'])
        self.assertEqual(decoded_dict.values(), [['a', 'b'], ['a', 'b']])
     
    def test_it_decodes_dicts_w_some_numbers(self):
        decoded_dict, rest = myBencoder.decode(self.dict_w_nums)
        self.assertEqual(decoded_dict.keys(), ['bar', 'foo'])
        self.assertEqual(decoded_dict.values(), ['spam', 42])  
        
    def test_it_decodes_dicts_w_nums_and_lists(self):
        decoded_dict, rest = myBencoder.decode(self.dict_w_nums_and_lists)
        self.assertEqual(decoded_dict.keys(), ['length', 'path'])
        self.assertEqual(decoded_dict.values(), [291, ['Distributed by Mininova.txt']])       
    
    def test_it_decodes_nested_dicts(self):
        pass
        
    def test_it_decodes_actual_bittorrent_files(self):
        decoded_dict, rest = myBencoder.decode(self.torrent)
        for key, value in decoded_dict.iteritems():
            print key + ' : ' + str(value)
        self.assertTrue(decoded_dict.keys())
#         self.assertEqual(decoded_dict.keys(), ['length', 'path'])
#         self.assertEqual(decoded_dict.values(), [291, ['Distributed by Mininova.txt']])       
    
                    
        
if __name__ == '__main__':
    unittest.main()
