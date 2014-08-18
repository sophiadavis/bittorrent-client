import binascii
import sys

import client
import metainfo
import peer_connection

connect = 0
announce = 1


class Session(object):
    def __init__(self, torrentFile):
        self.metainfo_file = metainfo.MetainfoFile(torrentFile)
        self.client = client.Client()
        self.sock = 0
        self.host = self.metainfo_file.announce_url_and_port[0]
        self.port = self.metainfo_file.announce_url_and_port[1]
    
    def connect_to_tracker(self):
        timeout = 1
        self.sock = self.client.open_socket_with_timeout(timeout)
        print 'Socket created.\n'
        
        connection_packet = self.client.make_connection_packet()
        response, address = self.client.send_packet(self.sock, self.host, self.port, connection_packet)
        return response
        
    def announce(self):
        announce_packet = self.client.make_announce_packet(self.metainfo_file.total_length, self.metainfo_file.bencoded_info_hash)
        response, address = self.client.send_packet(self.sock, self.host, self.port, announce_packet) 
        return response
    
    def get_torrent(self):
        connection_response = self.connect_to_tracker()
        connection_status = self.client.check_packet(connect, connection_response)
        self.check_status(connection_status, "connect")
        
        announce_response = self.announce()
        announce_status = self.client.check_packet(announce, announce_response)
        self.check_status(announce_status, "announce")
        
        peer_list = self.client.get_list_of_peers(announce_response)
                
        for i, peer in enumerate(peer_list):
            if peer[1] < 0:
                continue
            else:    
                current_peer = peer_list[i]
                peer = self.client.send_handshake(current_peer, self.metainfo_file.bencoded_info_hash)
                if not peer: 
                    print "*Peer not valid.\n"   
                    continue
                else:
                    print "*Peer valid:"
                    print "\tIP: " + str(peer.peer_ip)
                    print "\tPort: " + str(peer.peer_port)
                    print "\tPeer ID: " + str(peer.peer_id)
                    print
              
        self.sock.close()

    def check_status(self, status, failure):
        if status < 0:
            print "Session: " + failure
            sys.exit(1)

def main():
    s = Session('../../walden.torrent')
    s.get_torrent()

if __name__ == '__main__':
    main()