from collections import OrderedDict
import re

def main():
    print "Hello world"
    
# d4:spaml1:a1:bee' represents the dictionary { "spam" => [ "a", "b" ] } 
    
def decode(message):
    print 'Starting with: ' + message
    current = message[0]        
    if current is 'd':
        print "** DICT"
        token = OrderedDict()
        
        i = 1
        while message[i] is not 'e':
            key, rest = decode_next_string(message[i : ])
            value, rest = decode(rest)
            token[key] = value
            message = rest
            i = 0
        print "From dict: " + str(token) + ' ' + rest
        return token, rest[1 : ] # skip the dict's 'e'
    
    elif current is 'l':
        print "** LIST"
        token = []
        
        i = 1
        while message[i] is not 'e':
            item, rest = decode(message[i : ])
            print item, rest
            token.append(item)
            message = rest
            i = 0
        print "From list: " + str(token) + ' ' + rest[1 : ]
        return token, rest[1 : ] # skip the list's 'e'
    
    else:
        token, rest = decode_next_unit(message)
        print "From else: " + str(token) + ' ' + rest
        return token, rest 
                
            
def decode_next_unit(message):
    current = message[0]
    if current is 'i':
        print "** INT"
        token, rest = decode_next_int(message)
    
    elif current.isdigit():
        print "** STRING"
        token, rest = decode_next_string(message)
        message = rest
    
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

def decode_next_list(message, sofar):
    pass

def decode_next_dict(message, sofar):
    pass
        