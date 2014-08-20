import binascii
import client


MESSAGE_TYPE_DICT = {   'choke' : 0,
                        'unchoke' : 1,
                        'interested' : 2,
                        'not-interested' : 3,
                        'have' : 4,
                        'bitfield' : 5,
                        'request' : 6,
                        'piece' : 7,
                        'cancel' : 8,
                        'port' : 9    }



class PeerConnection(object):
    
    def __init__(self, peer_ip, peer_port, peer_id, sock):
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.peer_id = peer_id
        self.sock = sock
        self.status = 'choked'
        
    def __str__(self):
        return '%s:%i -- status: %s' % (str(self.peer_ip), self.peer_port, self.status)
    
    def _parse_choke(self, packet, length):
        self.status = 'choked'
        print 'choke'
        return "choke"
    
    def _parse_unchoke(self, packet, length):
        self.status = 'unchoked'
        print 'unchoked'
        return 'unchoked'
    
    def _parse_bitfield(self, packet, length):
        print "bitfield"
        print message
#         self.status = 'unchoked'
#         for i in message:
#             print binascii.unhexlify(i)
        return "bitfield"
    
    def _parse_have(self, packet, length):
        print "have"
        
#         self.status = 'unchoked'
#         for i in message:
#             print binascii.unhexlify(i)
        return "have"
        
    def parse_and_update_status_from_message(self, packet, length, id):
        print (length, id)
        MESSAGE_PARSE_DICT = {  0 : self._parse_choke,
                    1 : self._parse_unchoke,
#                         2 : parse_interested,
#                         3 : parse_uninterested,            
                    4 : self._parse_have,
                    5 : self._parse_bitfield }#,
#                         6 : parse_request,
#                         7 : parse_piece,
#                         8 : parse_cancel,
#                         9 : parse_port  }
    
    
#         from pudb import set_trace; set_trace()
        if int(id) in range(9):
            return MESSAGE_PARSE_DICT[id](packet, length)
        else:
            print "Message not recognized"

        



# class Message(object):
#     
#     def __init__(self, type, payload):
#         self.type = self._translate_type(type)
#         self.payload = payload
#         
#     def _translate_type(self, int_type):
#         return MESSAGE_TYPE_DICT[int_type]
#     
#     @property
#     def length(self):
#         return len(payload) #??? 

# class Message(object):
#     
#     def __init__(self, response, peer):
#         self.response = self.response
#         self.peer = peer
#     
#     def parse(self):
#         length_and_id = self.response[:5]
#         length, id = client.unpack_binary_string('>IB', length_and_id)
#         if id in MESSAGE_PARSE_DICT.keys():
#             MESSAGE_PARSE_DICT[id](response)
#         else:
#             print "Message not recognized"
#     
#     def parse_unchoke(self):
#         peer.status = 'unchoked'

    
        
  
    
    



