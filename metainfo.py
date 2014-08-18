def main():
    t = MetainfoFile('../../Wer ist wer bei Conny Van Ehlsing ... Gaijin PDF [mininova].torrent')
    print t
    

class MetainfoFile:
    ''' Represents information contained in a .torrent file '''
    def __init__(self, file_name):
        self.file_name = file_name
        self.bencoded_text = read_binary_file(file_name)
        self.parsed_text = decode(self.bencoded_text)[0] # add single underscore
        self.parsed_info_hash = self.parsed_text['info']
        self.bencoded_info_hash = encode(self.parsed_text['info']) # turn into readonly property

# or -- behave like dictionary, list, etc.
#     def __getitem__(self, key):
#         return 
        
    def __str__(self):
        decoded_text = ''
        for key, value in self.parsed_text.iteritems():
            if type(value) is not OrderedDict:
                decoded_text = decoded_text + key + ' : ' + str(value) + '\n'
            else:
                decoded_text = decoded_text + key + ' : ' + '\n'
                for key2, value2 in value.iteritems():
                    decoded_text = decoded_text + '------' + key2 + ' : ' + str(value2) + '\n'
        return decoded_text

    @property
    def total_length(self):
        total_length = 0
        for file in self.parsed_info_hash['files']:
            total_length += file['length']
        return total_length
    
    @property
    def announce_url_and_port(self):
        parsed = self.parsed_text['announce'].rstrip('/announce')
        port_index = parsed.rfind(':')
        slash_index = parsed.rfind('/')
        url = parsed[slash_index + 1 : port_index]
        port = parsed[port_index + 1 :]
        try:
            port = int(port)
        except ValueError as e:
            # TODO???
            pass
        return url, port
    
def read_binary_file(file_name):
    ''' Reads bytes from given file, returns binary string ''' 
    with open(file_name, "rb") as f:
        data = f.read() # remove context mnger??
        # or open(file name).read(), and wait for garbage collector
    return data   