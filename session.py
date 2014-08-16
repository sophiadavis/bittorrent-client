import client
import metainfo


class Session:
    def __init__(self, torrentFile):
        self.metainfo_file = metainfo.MetainfoFile(torrentFile)
        self.client = client.Client()
    
    def get_torrent(self):
        host, port = self.metainfo_file.get_announce_url_and_port()
    
        file = '../../walden.torrent'
        sock = self.client.open_nonblocking_socket()
        print 'Socket created.\n'

        while(1):           
            connection_packet = self.client.make_connection_packet()
            response, address = self.client.send_packet_to_tracker(sock, host, port, connection_packet)
            status = self.client.check_packet(0, response)
            if status < 0:
                print 'Deal with error'
            else:
                print 'Success!'
                announce_packet = self.client.make_announce_packet(self.metainfo_file.get_total_length(), self.metainfo_file.bencoded_info_hash)
                response, address = self.client.send_packet_to_tracker(sock, host, port, announce_packet) 
                print "******************************************"
                print "Response 2: " + str(response) 
                print "******************************************"
                print len(response)
                self.client.get_peers_from_response(response)
                break
              
        sock.close()

def main():
    s = Session('../../walden.torrent')
    s.get_torrent()

if __name__ == '__main__':
    main()