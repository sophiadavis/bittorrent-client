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
    
    def strategically_get_next_piece_index_and_block(self):
        current = self.next_request[:]
        self.requested.append(current)
        piece_index, byte_index = current
        
        block_index = int(byte_index / 2**14)
        
        current_piece = self.pieces_status_dict[piece_index]
        
        from pudb import set_trace; set_trace()
        if block_index == len(current_piece.block_list) - 1: # are there any blocks left?
            if piece_index == self.meta.num_pieces - 1: # are there any pieces left?
                if self.requested:
                    self.next_request = self.requested.pop[0][:] # start shuffling through outstanding requests
                else:
                    return "DONE"
            else:
                self.next_request = [piece_index + 1, 0]
        else:
            self.next_request = [piece_index, (block_index + 1) * 2**14]
        
        return current
        
    def _create_pieces_dict(self):
        d = OrderedDict()
        for piece_index in range(self.meta.num_pieces):
            d[piece_index] = Piece(piece_index, self.meta.piece_length, self.meta.request_blocks_per_piece, self.meta.pieces_hash)
        
        # last piece has a different number of blocks different
        bytes_remaining = self.meta.total_length % self.meta.piece_length
        blocks_remaining = int(math.ceil( float(bytes_remaining) / 2**14))
        d[self.meta.num_pieces] = Piece(self.meta.num_pieces, self.meta.piece_length, blocks_remaining, self.meta.pieces_hash)
        return d
        
        
    def process_piece(self, piece_index, begin, block):
        
        # THIS IS WRONG?
        block_index = int(begin / 2**14)
        current_piece = self.pieces_status_dict[piece_index]
        
        # maybe premature
        self.requested.remove([piece_index, begin]) 
        
        # save block into piece
        current_piece.block_list[block_index] = block
        
        current_piece.process_if_complete(self.download_filename)
        

class Piece(object):
    def __init__(self, index, piece_length, num_request_blocks, total_hash):
        self.index = index
        self.byte_index_in_file = piece_length * index
        self.hash = total_hash[index * 20 : (index * 20) + 20]
        self.block_list = [''] * num_request_blocks
        self.status = "incomplete"
        
    def __str__(self):
        return "Piece %i: %s \n ------ index in file: %i \n ------ hash: %s \n ------ block_list: %s" % (self.index, self.status, self.byte_index_in_file, self.hash, str(self.block_list))
        
    def process_if_complete(self, filename):
        if self.block_list.count('') == 0:
            self.status = "complete"
            
            if self.write_completed_piece(filename):
                print "yay"
            else:
                print "help"
        # return???
    
    def write_completed_piece(self, file_name):
        from pudb import set_trace; set_trace()
        complete_piece = ''.join(self.block_list)
        block_hash = hashlib.sha1(complete_piece).digest()
        if block_hash == self.hash:
            with open(file_name, "wb") as f:
                data = f.seek(self.byte_index_in_file)
                f.write(complete_piece)
            return True
        else:
            return False            
        
        
        
    

        
    