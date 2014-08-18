import client

class PeerConnection(object):
    
    def __init__(self, peer_ip, peer_port, peer_id, sock):
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.peer_id = peer_id
        self.sock = sock
    
    



