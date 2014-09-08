'''
Contains Session class to coordinate overall download process.
'''
import os
import os.path
import select
import socket
import sys

import client
import metainfo
import peer_connection
import torrent

class Session(object):
    ''' Coordinates download process. '''
    def __init__(self, meta, torrent_download):
        self.meta = meta
        self.client = client.Client()
        self.sock = 0
        self.host = self.meta.announce_url_and_port[0]
        self.port = self.meta.announce_url_and_port[1]
        self.torrent_download = torrent_download
    
    def connect_to_tracker(self):
        ''' Initiate communication with tracker (using Client). '''
        timeout = 1
        self.sock = client.open_socket_with_timeout(timeout)
        print 'Socket created.\n'
        
        connection_packet = self.client.make_connection_packet()
        response = self.client.send_packet(self.sock, self.host, self.port, connection_packet)
        return response
        
    def announce(self):
        ''' Send announce packet to tracker (using Client). '''
        announce_packet = self.client.make_announce_packet(self.meta.total_length, self.meta.bencoded_info_hash)
        response = self.client.send_packet(self.sock, self.host, self.port, announce_packet) 
        return response
    
    def check_status(self, status, failure):
        ''' Generic error-handling. '''
        if status < 0:
            print "Session: " + failure
            sys.exit(1)
    
    def get_torrent(self):
        ''' Coordinate entire file download process. '''
        
        CONNECT_ID = 0
        ANNOUNCE_ID = 1

        connection_response = self.connect_to_tracker()
        connection_status = self.client.check_packet(CONNECT_ID, connection_response)
        self.check_status(connection_status, "connect")
        
        announce_response = self.announce()
        announce_status = self.client.check_packet(ANNOUNCE_ID, announce_response)
        self.check_status(announce_status, "announce")
        
        peer_list = self.client.get_list_of_peers(announce_response)
                
        waiting_for_read = []
        waiting_for_write = []
        for peer_info_list in peer_list:   
            peer = self.client.build_peer(peer_info_list, self.meta.num_pieces, self.meta.bencoded_info_hash, self.torrent_download)
            peer.schedule_handshake(self.client.peer_id)
            waiting_for_read.append(peer)
            try:
                peer.sock.connect((peer.ip, peer.port))
            except socket.error as e:
                print e
                pass
        
        while waiting_for_read or waiting_for_write:
            waiting_for_write = []
            for peer in waiting_for_read:
                if peer.out_buffer:
                    waiting_for_write.append(peer)
            
            readable, writeable, errors = select.select(waiting_for_read, waiting_for_write, [])
            print "\nSelected -- read: %i, write: %i, errors: %i" % (len(readable), len(writeable), len(errors))
             
            for peer in writeable:
                print "Writing: " + str(peer)
                peer.send_from_out_buffer()
            
            for peer in readable:
                print "Reading: " + str(peer)
                try:
                    response = peer.sock.recv(1024)
                    if not response:
                        waiting_for_read.remove(peer)
                        continue
                except socket.error as e:
                    print e
                    continue
                peer.in_buffer += response
                status = peer.handle_in_buffer()
                while status:
                    if status == "DONE":
                        self.sock.close()
                        return
                    status = peer.handle_in_buffer()
            
            if self.torrent_download.status() == "complete":
                self.sock.close()
                return

    def transfer_file_contents(self, temp_filename):
        ''' Write downloaded bytes (stored in temp file) into appropriate files. '''
        if self.meta.type == "single":
            full_path = "../../" + self.meta.base_file_name
            print "Writing to file %s" % full_path
            os.rename(temp_filename, full_path)
        else:
            current_location = 0
            for file_index in self.meta.file_info_dict.keys():
                f = self.meta.file_info_dict[file_index]
                path_elements = file[0]
                length = file[1]
        
                path = "../../" + self.meta.base_file_name
                file_name = path_elements.pop()
                for d in path_elements:
                    path = os.path.join(path, dir)
                
                if not os.path.exists(path):
                    os.makedirs(path) 
                
                try:
                    full_path = os.path.join(path, file_name)
                    with open(temp_filename, "rb") as f:
                        f.seek(current_location)
                        file_data = f.read(length)
                
                    print "Writing %i bytes to f %s" % (length, full_path)
                    with open(full_path, "wb") as f:
                        f.write(file_data)
        
                    current_location += length
                except Exception as e:
                    print "Error writing to file: %s" % file_name
                    print e
        
                
                

def main():
    if len(sys.argv) < 2 or sys.argv[1][-8:] != ".torrent":
        print "Usage: python session.py metainfo_file.torrent"
    else: 
        metainfo_filename = sys.argv[1]
        meta = metainfo.MetainfoFile(metainfo_filename)
        temp_filename = '../../temp.bytes'
        open(temp_filename, 'w').close()
        
        torrent_download = torrent.Torrent(meta, temp_filename)
        s = Session(meta, torrent_download)
        
        s.get_torrent()
        s.transfer_file_contents(temp_filename)
        
        os.remove(temp_filename)

if __name__ == '__main__':
    main()