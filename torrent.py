from collections import OrderedDict
import hashlib
import math

import metainfo

class Torrent(object):
    
    def __init__(self, meta, download_filename):
        self.meta = meta
        self.pieces_status_dict = self._create_pieces_dict()
        self.download_filename = download_filename
        self.next_request = [0, 0] # piece_index, block_number
        self.requested = []
        self.pieces = ['unrequested'] * (self.meta.num_pieces)
        # plus 1?
    
    def strategically_get_next_piece_index_and_block(self):
        current = self.next_request[:]
        
        if current == "DONE":
            return "DONE"
        
        self.requested.append(current)
        piece_index, byte_index = current
        block_index = int(byte_index / 2**14)
        current_piece = self.pieces_status_dict[piece_index]
        
        current_piece.block_request_status_list[block_index] = 1
        current_piece.update_status(self.pieces)
        # THIS IS CONFUSING
        
#         if self.pieces.count("complete") > 76:
#             from pudb import set_trace; set_trace()
        
        if 'semi_requested' in self.pieces:
            next_piece_index = self.pieces.index('semi_requested')
            next_block_index = current_piece.next_block_index()
        elif 'unrequested' in self.pieces:
            next_piece_index = self.pieces.index('unrequested')
            next_block_index = 0
        elif 'all_requested' in self.pieces:
            if self.requested:
                next_piece_index, next_block_index = self.requested.pop(0)
            else:
                self.next_request = "DONE"
                return current
        else:
            self.next_request = "DONE"
            return current
        self.next_request = [next_piece_index, next_block_index * 2**14]
        return current
        
    def _create_pieces_dict(self):
        d = OrderedDict()
        for piece_index in range(self.meta.num_pieces - 1): # -1 ???? wtf?
            d[piece_index] = Piece(piece_index, self.meta.piece_length, self.meta.request_blocks_per_piece, self.meta.pieces_hash)
        
        # last piece has a different number of blocks different
        bytes_remaining = self.meta.total_length % self.meta.piece_length
        blocks_remaining = int(math.ceil( float(bytes_remaining) / 2**14))
        last_piece_index = self.meta.num_pieces - 1
        d[last_piece_index] = Piece(last_piece_index, self.meta.piece_length, blocks_remaining, self.meta.pieces_hash)
        return d
        
        
    def process_piece(self, piece_index, begin, block):
        print "~~~~~~~~~~ Processing piece: " + str(piece_index)
#         from pudb import set_trace; set_trace()
        
        # THIS IS WRONG?
        block_index = int(begin / 2**14)
        current_piece = self.pieces_status_dict[piece_index]
        
        # maybe premature
        if [piece_index, begin] in self.requested:
            self.requested.remove([piece_index, begin]) 
#         else:
#             # we already removed it -- so we already saved it
#             return
        
        # save block into piece
        current_piece.block_data_list[block_index] = block
        
        current_piece.update_status(self.pieces)
        
        print "Piece %i -- %s" % (current_piece.index, current_piece.status)
        
        if current_piece.status == "complete":
            if not current_piece.write_completed_piece(self.download_filename):
                current_piece.reset(self.pieces)
                
    def status(self):
        if self.pieces.count("complete") > 76:
            print self.pieces
#             from pudb import set_trace; set_trace()
        if len(self.pieces) == self.pieces.count("complete"):
            return "complete"
        else:
            return "incomplete"
        
        

class Piece(object):
    def __init__(self, index, piece_length, num_request_blocks, total_hash):
        self.index = index
        self.byte_index_in_file = piece_length * index
        self.hash = total_hash[index * 20 : (index * 20) + 20]
        self.block_request_status_list = [0] * num_request_blocks
        self.block_data_list = [''] * num_request_blocks
        self.status = "unrequested" # unrequested, semi_requested, all_requested, complete
        
    def __str__(self):
        return "Piece %i: %s \n ------ index in file: %i \n ------ hash: %s \n ------ block_data_list: %s" % (self.index, self.status, self.byte_index_in_file, self.hash, str(self.block_data_list))
     
    def update_status(self, pieces_list):
        if self.block_data_list.count('') == 0:
            self.status = "complete"
        elif 1 in self.block_request_status_list and 0 in self.block_request_status_list:
            self.status = "semi_requested"
        elif self.block_request_status_list.count(0) == 0:
            self.status = "all_requested"
        else:
            self.status = "unrequested"
        pieces_list[self.index] = self.status
    
    def reset(self, pieces_list):
        self.status = "unrequested"
        pieces_list[self.index] = self.status
        self.block_request_status_list = [0] * num_request_blocks
        self.block_data_list = [''] * num_request_blocks
    
    def next_block_index(self):
        if 0 in self.block_data_list:
            return self.block_data_list.index(0)
        else:
            return -1
    
    def write_completed_piece(self, file_name):
        complete_piece = ''.join(self.block_data_list)
        block_hash = hashlib.sha1(complete_piece).digest()
        if block_hash == self.hash:
            print "~~~~~~~~~~ Verified: " + str(self.index)
            with open(file_name, "r+b") as f:
                f.seek(self.byte_index_in_file)
                f.write(complete_piece)
            return True
        else:
            print "~~~~~~~~~~ Unverified: " + str(self.index)
            return False            
        
        
        
    

        
    