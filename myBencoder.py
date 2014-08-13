import re

# class BenDecoder:

wrapped_list_pattern = re.compile(r"(l.*e)")
unwrapped_list_pattern = re.compile(r"l(.*)e")

wrapped_int_pattern = re.compile(r"(i-?\d*e)")
unwrapped_int_pattern = re.compile(r"i(-?\d*)e")

# wrapped_string_pattern = re.compile(r"(\d+:.*)") #r"(\d+:.*)([\dlied]:.*)"
wrapped_string_pattern = re.compile(r"(\d+:.*)$|\d+:")
wrapped_string_pattern = re.compile(r"(\d+:.*)")
unwrapped_string_pattern = re.compile(r"\d+:(.*)")
# unwrapped_string_pattern = re.compile(r"\d+:(.*)($|(\d+:))")

def main():
    print "Hello world"
    
# d4:spaml1:a1:bee' represents the dictionary { "spam" => [ "a", "b" ] } 
    
def decode(message):
    print message
    while message:
        # 'unwrap' datastructure from outside in
        if message[0] == 'l':
            list_match = re.match(wrapped_list_pattern, message)
            return_if_none(list_match)
            return decode_list(list_match.group(1))
        elif message[0] == 'i':
            int_match = re.match(wrapped_int_pattern, message)
            return_if_none(int_match)
            return decode_int(int_match.group(1))
        else: # string
            str_match = re.match(wrapped_string_pattern, message)
            return_if_none(str_match)
            return decode_strings(str_match.group(1))

def decode_strings(b_str):
    str_list = []
    while b_str:
        print "str_list is " + str(str_list)
        c = b_str.find(':')
        b_str = b_str[c + 1 :]
        c2 = b_str.find(':')
        print c, c2
        if c2 < 0:
            print "if  "
            print b_str
            str_list.append(b_str)
            break
        else:
            print "else  "
            print b_str[ : c2]
            m = re.match(r"^(\D*)", b_str[ : c2])
            return_if_none(m)
            str_list.append(m.group(1))
    return str_list
#     str_match = re.match(unwrapped_string_pattern, b_str) # returns None if no match
#     return_if_none(str_match)
#     return str_match.group(1)

def decode_int(b_int):
    int_match = re.match(unwrapped_int_pattern, b_int)
    return_if_none(int_match)
    return int(int_match.group(1))

def decode_list(b_list):
    decoded = []
    contents = re.match(unwrapped_list_pattern, b_list)
    return_if_none(contents)
    item = decode(contents.group(1))
    while item:
        decoded.append(item)
    return decoded
    
def return_if_none(match):
    if match is None:
        print "No match!"
        return None
        