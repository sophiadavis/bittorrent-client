import unittest
import re

import myBencoder

class BencodeTests(unittest.TestCase):
    
    def setUp(self):
        self.b_list = 'l4:spam4:eggse'
        self.b_str = '17:publisher-webpage'
        self.b_int = 'i3e'
        self.b_neg_int = 'i-3e'
    
    # Test regex patterns
#     def test_wrapped_list_regex_pattern_works(self):
#         m = re.search(myBencoder.wrapped_list_pattern, self.b_list)
#         self.assertEqual(m.group(1), self.b_list)
#         
#     def test_unwrapped_list_regex_pattern_works(self):    
#         m = re.search(myBencoder.unwrapped_list_pattern, self.b_list)
#         self.assertEqual(m.group(1), '4:spam4:eggs')
#     
#     def test_wrapped_int_regex_pattern_works(self): 
#         m = re.search(myBencoder.wrapped_int_pattern, self.b_int)
#         self.assertEqual(m.group(1), self.b_int)
#     
#     def test_wrapped_int_regex_pattern_works_with_negatives(self): 
#         m = re.search(myBencoder.wrapped_int_pattern, self.b_neg_int)
#         self.assertEqual(m.group(1), self.b_neg_int)
#         
#     def test_unwrapped_int_regex_pattern_works(self):    
#         m = re.search(myBencoder.unwrapped_int_pattern, self.b_int)
#         self.assertEqual(m.group(1), '3')
#         
#     def test_unwrapped_int_regex_pattern_works_with_negatives(self):    
#         m = re.search(myBencoder.unwrapped_int_pattern, self.b_neg_int)
#         self.assertEqual(m.group(1), '-3')
# 
#     def test_wrapped_string_regex_pattern_works(self): 
#         m = re.search(myBencoder.wrapped_string_pattern, self.b_str)
#         self.assertEqual(m.group(1), self.b_str)
#     
#     def test_unwrapped_string_regex_pattern_works(self): 
#         m = re.search(myBencoder.unwrapped_string_pattern, self.b_str)
#         self.assertEqual(m.group(1), 'publisher-webpage')
#         
#     def test_wrapped_int_regex_pattern_matches_only_first_instance(self):    
#         m = re.search(myBencoder.wrapped_int_pattern, self.b_int + self.b_int)
#         self.assertEqual(m.group(1), self.b_int) 
#     
#     def test_unwrapped_int_regex_pattern_matches_only_first_instance(self):    
#         m = re.search(myBencoder.unwrapped_int_pattern, self.b_int + self.b_int)
#         self.assertEqual(m.group(1), '3')    
#     
#     def test_wrapped_string_regex_pattern_matches_only_first_instance(self): 
#         m = re.search(myBencoder.wrapped_string_pattern, self.b_str + self.b_str)
#         self.assertEqual(m.group(1), self.b_str)
#     
#     def test_unwrapped_string_regex_pattern_matches_only_first_instance(self): 
#         m = re.search(myBencoder.unwrapped_string_pattern, self.b_str + self.b_str)
#         self.assertEqual(m.group(1), 'publisher-webpage')
    
    
    # test decoding of units (ints and strings)
    def test_it_decodes_ints(self):
        decoded_int = myBencoder.decode_int(self.b_int)
        self.assertEqual(decoded_int, 3)
    
    def test_it_decodes_negatives(self):
        decoded_int = myBencoder.decode_int(self.b_neg_int)
        self.assertEqual(decoded_int, -3)
        
    def test_it_decodes_strings(self):
        decoded_str = myBencoder.decode_strings(self.b_str)
        self.assertEqual(decoded_str, ['publisher-webpage'])
        
    def test_it_decodes_strings_2(self):
        decoded_str = myBencoder.decode_strings(self.b_str + self.b_str + self.b_str)
        self.assertEqual(decoded_str, ['publisher-webpage', 'publisher-webpage', 'publisher-webpage'])
    
        
#     def test_it_decodes_lists(self):
#         decoded_list = myBencoder.decode(self.b_list)
#         self.assertEqual(decoded_list, ['spam', 'eggs'])
        
#     def test_it_decodes_nested_lists(self):
                
        
if __name__ == '__main__':
    unittest.main()
