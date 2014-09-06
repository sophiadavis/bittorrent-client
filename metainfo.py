'''
Contains Metainfo class, a wrapper for information found in a .torrent metainfo file.
'''
import math
from collections import OrderedDict

import bencoder

def main():
    t = MetainfoFile('../../Wer ist wer bei Conny Van Ehlsing ... Gaijin PDF [mininova].torrent')
    print t
    

class MetainfoFile(object):
    ''' Represents information contained in a .torrent file. '''
    
    def __init__(self, file_name):
        # Text
        self._bencoded_text = read_binary_file(file_name)
        self._parsed_text = bencoder.decode(self._bencoded_text)[0]
        self._parsed_info_hash = self._parsed_text['info']
        self.bencoded_info_hash = bencoder.encode(self._parsed_info_hash) # turn into readonly property
        
        # File information
        self.file_info_dict = self._get_file_info_dict()
        self.base_file_name = self._parsed_info_hash['name']
        self.type = "single" if len(self.file_info_dict.keys()) == 1 else "multiple"
        
        # Length and piece information
        self.total_length = self._get_total_length()
        self.piece_length = self._parsed_info_hash['piece length']
        self.num_pieces = int(len(self._parsed_info_hash['pieces']) / 20)
        self.request_blocks_per_piece = int(math.ceil( float(self.piece_length) / 2**14))
        self.pieces_hash = self._parsed_info_hash['pieces']
        
    def __str__(self):
        decoded_text = ''
        for key, value in self._parsed_text.iteritems():
            if type(value) is not OrderedDict:
                decoded_text = decoded_text + key + ' : ' + str(value) + '\n'
            else:
                decoded_text = decoded_text + key + ' : ' + '\n'
                for key2, value2 in value.iteritems():
                    decoded_text = decoded_text + '------' + key2 + ' : ' + str(value2) + '\n'
        return decoded_text
    
    @property
    def announce_url_and_port(self):
        ''' Determines the url and port of a tracker (if multiple trackers are listed
            the metainfo file, only information about the first one is returned. '''
        parsed = self._parsed_text['announce'].rstrip('/announce')
        port_index = parsed.rfind(':')
        slash_index = parsed.rfind('/')
        url = parsed[slash_index + 1 : port_index]
        port = parsed[port_index + 1 :]
        try:
            port = int(port)
        except ValueError as e:
            port = 80 # just a guess...
        return url, port
    
    def _get_file_info_dict(self):
        ''' Parses information about each file contained in a torrent download, 
            saving the file length and path information into an ordered dictionary. '''
        d = OrderedDict()
        if 'length' in self._parsed_info_hash.keys():
            d[0] = [self._parsed_info_hash['name'], self._parsed_info_hash['length']]
        else:
            for i, file in enumerate(self._parsed_info_hash['files']):
                d[i] = [file['path'], file['length']]
        return d
    
    def _get_total_length(self):
        ''' Calculates the total length of the torrent download from the lengths of each
            included file. '''
        total_length = 0
        for piece_index in self.file_info_dict.keys():
            total_length += self.file_info_dict[piece_index][1]
        return total_length
            
def read_binary_file(file_name):
    ''' Reads bytes from given file, returns binary string ''' 
    with open(file_name, "rb") as f:
        data = f.read()
    return data   