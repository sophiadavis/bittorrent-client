# import binascii
from collections import OrderedDict
import re

def main():
    t = MetainfoFile('../../Wer ist wer bei Conny Van Ehlsing ... Gaijin PDF [mininova].torrent')
    print t
    

class MetainfoFile:
    ''' Represents information contained in a .torrent file '''
    def __init__(self, file_name):
        self.file_name = file_name
        self.bencoded_text = read_binary_file(file_name)
        self.parsed_text = decode(self.bencoded_text)[0]
        self.parsed_info_hash = self.parsed_text['info']
        self.bencoded_info_hash = encode(self.parsed_text['info'])
        
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

    def get_total_length(self):
        total_length = 0
        for file in self.parsed_info_hash['files']:
            total_length += file['length']
        return total_length
    
    def get_announce_url_and_port(self):
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
        byte = f.read(1)
        data = byte
        while byte != "":
            byte = f.read(1)
            data += byte
    return data   
        
###################################
# Functions for decoding bencoded data
###################################        
def decode(message):
    ''' Decodes b-encoded text, recursively parses lists and dictionaries '''
    ''' All dictionaries are represented as OrderedDicts, lists as Python lists, strings as strings, ints as ints '''
    ''' Returns 'highest' parsed unit and the remaining b-encoded text ''' 
    current = message[0]        
    if current is 'd':
        token = OrderedDict()
        
        i = 1
        while message[i] is not 'e':
            key, rest = decode_next_string(message[i : ])
            value, rest = decode(rest)
            token[key] = value
            message = rest
            i = 0
        return token, rest[1 : ] # skip the dict's 'e'
    
    elif current is 'l':
        token = []
        
        i = 1
        while message[i] is not 'e':
            item, rest = decode(message[i : ])
            token.append(item)
            message = rest
            i = 0
        return token, rest[1 : ] # skip the list's 'e'
    
    else:
        token, rest = decode_next_unit(message)
        return token, rest 
                
            
def decode_next_unit(message):
    ''' Helper method for decoding of b-encoded texts '''
    ''' Returns 'highest' parsed unit and the remaining b-encoded text '''        
    current = message[0]
    if current is 'i':
        token, rest = decode_next_int(message)
    
    elif current.isdigit():
        token, rest = decode_next_string(message)
        message = rest
    
    ## handle this case???
    else:
        token = 'oops'
        rest = message
        print "PANIC" # TODO
        
    return token, rest


def decode_next_string(message):
    ''' Helper method for decoding of b-encoded texts '''
    ''' Returns 'highest' parsed unit and the remaining b-encoded text ''' 
    l = re.match(r"^(\d*):", message).group(1) # there is at least one digit, so this can't be None
    l = int(l)
    
    colon = message.find(':')
    decoded = message[(colon + 1) : (colon + l + 1)]
    rest = message[(colon + l + 1) : ]
    
    return decoded, rest


def decode_next_int(message):
    ''' Helper method for decoding of b-encoded texts '''
    ''' Returns 'highest' parsed unit and the remaining b-encoded text ''' 
    int_str = ''
    i = 1
    while message[i] is not 'e':
        int_str += message[i]
        i += 1;
    return int(int_str), message[(i + 1) : ]
    
###################################
# Functions for encoding normal text as bencoded data
###################################
def encode(message):
    if type(message) is list:
        encoded = 'l'
        for item in message:
            encoded += encode(item)
        encoded += 'e'
        
    elif type(message) is OrderedDict:
        encoded = 'd'
        for key, value in message.iteritems():
            encoded += encode_string(key)
            encoded += encode(value)
        encoded += 'e'
        
    else:
        encoded = encode_unit(message)
    return encoded
        
def encode_unit(unit):
    if type(unit) is int:
        return encode_int(unit)
    elif type(unit) is str:
        return encode_string(unit)
    else:
        print "PANIC" # TODO  
        return 'oops'      

def encode_int(i):
    return 'i' + str(i) + 'e'

def encode_string(s):
    prefix = len(s)
    return str(prefix) + ':' + s

if __name__ == '__main__':
    main()