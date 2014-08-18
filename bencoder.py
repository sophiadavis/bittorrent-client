from collections import OrderedDict
import re
        
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
            key, rest = _decode_next_string(message[i : ])
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
        token, rest = _decode_next_unit(message)
        return token, rest 
                
            
def _decode_next_unit(message):
    ''' Helper method for decoding of b-encoded texts '''
    ''' Returns 'highest' parsed unit and the remaining b-encoded text '''        
    current = message[0]
    if current is 'i':
        token, rest = _decode_next_int(message)
    
    elif current.isdigit():
        token, rest = _decode_next_string(message)
        message = rest
    
    ## handle this case???
    else:
        token = 'oops'
        rest = message
        print "PANIC" # TODO
        
    return token, rest


def _decode_next_string(message):
    ''' Helper method for decoding of b-encoded texts '''
    ''' Returns 'highest' parsed unit and the remaining b-encoded text ''' 
    l = re.match(r"^(\d*):", message).group(1) # there is at least one digit, so this can't be None
    l = int(l)
    
    colon = message.find(':')
    decoded = message[(colon + 1) : (colon + l + 1)]
    rest = message[(colon + l + 1) : ]
    
    return decoded, rest


def _decode_next_int(message):
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
            encoded += _encode_string(key)
            encoded += encode(value)
        encoded += 'e'
        
    else:
        encoded = _encode_unit(message)
    return encoded
        
def _encode_unit(unit):
    if type(unit) is int:
        return _encode_int(unit)
    elif type(unit) is str:
        return _encode_string(unit)
    else:
        print "PANIC" # TODO  
        return 'oops'      

def _encode_int(i):
    return 'i' + str(i) + 'e'

def _encode_string(s):
    prefix = len(s)
    return str(prefix) + ':' + s

if __name__ == '__main__':
    main()