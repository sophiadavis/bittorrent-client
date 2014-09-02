import bencoder
from collections import OrderedDict

def main():
    t = MetainfoFile('../../Wer ist wer bei Conny Van Ehlsing ... Gaijin PDF [mininova].torrent')
    print t
    

class MetainfoFile(object):
    ''' Represents information contained in a .torrent file '''
    def __init__(self, file_name):
        self.file_name = file_name
        self.bencoded_text = read_binary_file(file_name)
        self._parsed_text = bencoder.decode(self.bencoded_text)[0] # add single underscore
        self._parsed_info_hash = self._parsed_text['info']
        self.bencoded_info_hash = bencoder.encode(self._parsed_info_hash) # turn into readonly property
        self.num_pieces = len(self._parsed_info_hash['pieces']) / 20
        self.length_dict = self._get_length_dict()
        self.total_length = self._get_total_length()
        
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
        parsed = self._parsed_text['announce'].rstrip('/announce')
        port_index = parsed.rfind(':')
        slash_index = parsed.rfind('/')
        url = parsed[slash_index + 1 : port_index]
        port = parsed[port_index + 1 :]
        try:
            port = int(port)
        except ValueError as e:
            port = 80 # ??
        return url, port
    
    def _get_length_dict(self):
        d = {}
        if 'length' in self._parsed_info_hash.keys():
            d[0] = self._parsed_info_hash['length']
        else:
            for i, file in enumerate(self._parsed_info_hash['files']):
                d[i] = file['length']
        return d
    
    def _get_total_length(self):
        total_length = 0
        for piece_index in self.length_dict.keys():
            total_length += self.length_dict[piece_index]
        return total_length
    
def read_binary_file(file_name):
    ''' Reads bytes from given file, returns binary string ''' 
    with open(file_name, "rb") as f:
        data = f.read() # remove context mnger??
        # or open(file name).read(), and wait for garbage collector
    return data   