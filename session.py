import sys

import client
import metainfo

connect = 0
announce = 1


class Session(object):
    def __init__(self, torrentFile):
        self.metainfo_file = metainfo.MetainfoFile(torrentFile)
        self.client = client.Client()
    
    def get_torrent(self):
        host, port = self.metainfo_file.announce_url_and_port
    
        timeout = 1
        sock = self.client.open_socket_with_timeout(timeout)
        print 'Socket created.\n'

        while(1):           
            connection_packet = self.client.make_connection_packet()
            response, address = self.client.send_packet_to_tracker(sock, host, port, connection_packet)
            status = self.client.check_packet(connect, response)
            if status < 0:
                print 'Deal with error'
                sys.exit(1)
            print 'Success!'
            announce_packet = self.client.make_announce_packet(self.metainfo_file.total_length, self.metainfo_file.bencoded_info_hash)
            response, address = self.client.send_packet_to_tracker(sock, host, port, announce_packet) 
            print "******************************************"
            print "Response 2: " + str(response) 
            print "******************************************"
            print len(response)
            status = self.client.check_packet(announce, response)
            print status
            break
              
        sock.close()

def main():
    s = Session('../../walden.torrent')
    s.get_torrent()

if __name__ == '__main__':
    main()