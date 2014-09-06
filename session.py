import binascii
import os
import os.path
import select
import socket
import sys

import client
import metainfo
import peer_connection
import torrent

connect = 0
announce = 1


class Session(object):
    def __init__(self, meta, shared_torrent_status_tracker):
        self.meta = meta
        self.client = client.Client()
        self.sock = 0
        self.host = self.meta.announce_url_and_port[0]
        self.port = self.meta.announce_url_and_port[1]
        self.shared_torrent_status_tracker = shared_torrent_status_tracker
    
    def connect_to_tracker(self):
        timeout = 1
        self.sock = client.open_socket_with_timeout(timeout)
        print 'Socket created.\n'
        
        connection_packet = self.client.make_connection_packet()
        response, address = self.client.send_packet(self.sock, self.host, self.port, connection_packet)
        return response
        
    def announce(self):
        announce_packet = self.client.make_announce_packet(self.meta.total_length, self.meta.bencoded_info_hash)
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
                
        waiting_for_read = []
        waiting_for_write = []
#         from pudb import set_trace; set_trace()
        for peer_info_list in peer_list:   
            peer = self.client.build_peer(peer_info_list, self.meta.num_pieces, self.meta.bencoded_info_hash, self.shared_torrent_status_tracker)
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
#             print "selected: "
            print len(readable), len(writeable), len(errors)
            
            print "writeables" 
            for peer in writeable:
                print peer
                success = peer.send_from_out_buffer()
                if not success:
                    print "could not send"
                    pass
                else:
                    print "SENT"
            
            
            for peer in readable:
#                 from pudb import set_trace; set_trace()
                print peer
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
                        return
                    status = peer.handle_in_buffer()
            
            if self.shared_torrent_status_tracker.status() == "complete":
                self.sock.close()
                return

    def check_status(self, status, failure):
        if status < 0:
            print "Session: " + failure
            sys.exit(1)

    def transfer_file_contents(self, temp_filename):
#         from pudb import set_trace; set_trace()
        if self.meta.type == "single":
            full_path = "../../" + self.meta.base_file_name
            print "Writing to file %s" % full_path
            os.rename(temp_filename, full_path)
        else:
            current_location = 0
            for file_index in self.meta.file_info_dict.keys():
                file = self.meta.file_info_dict[file_index]
                path_elements = file[0]
                length = file[1]
        
                path = "../../" + self.meta.base_file_name
                file_name = path_elements.pop()
                for dir in path_elements:
                    path = os.path.join(path, dir)
                
                if not os.path.exists(path):
                    os.makedirs(path) 
                
                try:
                    full_path = os.path.join(path, file_name)
                    with open(temp_filename, "rb") as f:
                        print "Tell", f.tell()
                        f.seek(current_location)
                        print "Tell", f.tell()
                        file_data = f.read(length)
                        print "Tell", f.tell()
                
                    print "Writing %i bytes to file %s" % (length, full_path)
                    with open(full_path, "wb") as f:
                        f.write(file_data)
        
                    current_location += length
                except Exception as e:
                    print "Error writing to file"
                    print e
                    from pudb import set_trace; set_trace()
                    return
        
                
                

def main():
#     metainfo_filename = '../../treasure_island.torrent'
#     metainfo_filename = '../../tom.torrent'
    metainfo_filename = '../../voltaire.torrent'
#     metainfo_filename = '../../walden.torrent'
    meta = metainfo.MetainfoFile(metainfo_filename)
    temp_filename = '../../temp.bytes'
    open(temp_filename, 'a').close()
    shared_torrent_status_tracker = torrent.Torrent(meta, temp_filename)
    s = Session(meta, shared_torrent_status_tracker)
#     s.get_torrent()
    s.transfer_file_contents(temp_filename)
#     os.remove(temp_filename)

if __name__ == '__main__':
    main()