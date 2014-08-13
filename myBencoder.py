from collections import OrderedDict
import re

def main():
    print "Hello world"

class MetainfoFile:
    def __init__(self, file_name):
        self.file_name = file_name
        self.text = read_binary_file(file_name)
        self.decoded = decode(self.text)
    
def read_binary_file(file_name):
    with open(file_name, "rb") as f:
        byte = f.read(1)
        data = byte
        while byte != "":
            byte = f.read(1)
            data += byte
    return data   
        
def decode(message):
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
        print "MISTAKE"
        
    return token, rest

def decode_next_string(message):
    l = re.match(r"^(\d*):", message).group(1) # there is at least one digit, so this can't be None
    l = int(l)
    
    colon = message.find(':')
    decoded = message[(colon + 1) : (colon + l + 1)]
    rest = message[(colon + l + 1) : ]
    
    return decoded, rest

def decode_next_int(message):
    int_str = ''
    i = 1
    while message[i] is not 'e':
        int_str += message[i]
        i += 1;
    return int(int_str), message[(i + 1) : ]
        