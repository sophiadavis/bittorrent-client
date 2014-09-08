'''
Contains:
    - Torrent class to manage overall status of the current download
    - Piece class to handle the status of each piece of the download, as well as
        how each piece should be requested and written to file
'''
import hashlib
import math

import metainfo
from constants import POLITE_REQUEST_SIZE

class Torrent(object):
    ''' Contains status of download and functions to determine which piece should be
        requested next.'''

    def __init__(self, meta, download_filename):
        self.meta = meta
        self.download_filename = download_filename
        self.requested = []
        self.pieces = self._create_pieces()

    def next_fresh_request(self):
        ''' Returns a request for any pieces/blocks that have not yet been completely requested,
            or None, if all blocks have been requested at least once. '''
        piece = (next((piece for piece in self.pieces if piece.status == 'semi_requested'), None) or
                 next((piece for piece in self.pieces if piece.status == 'unrequested'), None))
        if piece:
            next_piece_index = piece.index
            next_block_index = piece.next_unrequested_block_index()
            next_block_length = piece.block_request_sizes_list[next_block_index]

            piece.block_request_status_list[next_block_index] = 1

            return [next_piece_index, next_block_index * POLITE_REQUEST_SIZE, next_block_length]
        else:
            return None

    def next_recycled_request(self):
        ''' Returns a request for next outstanding piece/block. '''
        outstanding = next((request for request in self.requested if self.pieces[request[0]].status not in ['written', 'complete']), None)
        return outstanding

    def strategically_get_next_request(self):
        ''' Returns a request.
            First, pieces are requested in order. Once all pieces have been requested,
                outstanding pieces are re-requested.
            All scheduled requests are stored in self.requested. '''
        next_request = self.next_fresh_request()
        if not next_request:
            next_request = self.next_recycled_request()
            if not next_request:
                return "DONE"
        self.requested.append(next_request)
        return next_request

    def _create_pieces(self):
        ''' Creates a list of all Piece objects in the current download. '''
        piece_list = []
        
        for piece_index in range(self.meta.num_pieces - 1):
        
            # last block may have different number of bytes
            last_block_remainder = self.meta.piece_length % ((self.meta.request_blocks_per_piece) * POLITE_REQUEST_SIZE)
            bytes_in_last_block = POLITE_REQUEST_SIZE if last_block_remainder == 0 else 0
            block_request_sizes_list = [POLITE_REQUEST_SIZE] * (self.meta.request_blocks_per_piece - 1) + [bytes_in_last_block]
            
            piece = Piece(piece_index, self.meta.piece_length, self.meta.request_blocks_per_piece,
                          self.meta.pieces_hash, block_request_sizes_list)
            piece_list.append(piece)

        # last piece has different number of bytes
        bytes_remaining = self.meta.total_length % self.meta.piece_length
        blocks_remaining = int(math.ceil(float(bytes_remaining) / POLITE_REQUEST_SIZE))
        bytes_in_last_block = bytes_remaining - ((blocks_remaining - 1) * POLITE_REQUEST_SIZE)
        block_request_sizes_list = [POLITE_REQUEST_SIZE] * (blocks_remaining - 1) + [bytes_in_last_block]

        last = Piece(self.meta.num_pieces - 1, self.meta.piece_length, blocks_remaining, self.meta.pieces_hash, block_request_sizes_list)
        piece_list.append(last)

        return piece_list


    def process_piece(self, piece_index, begin, block):
        ''' Processes an incoming block of a piece, writing the piece to file once all blocks
            are present. '''
        block_index = int(begin / POLITE_REQUEST_SIZE)
        current_piece = self.pieces[piece_index]

        print "~~~~~~~~~~ Processing piece: " + str(current_piece)

        # remove piece/block from requested list
        outstanding = [request for request in self.requested if request[0:2] == [piece_index, begin]]
        if outstanding:
            for request in outstanding:
                self.requested.remove(request)

        if current_piece.status != "written":
            current_piece.block_data_list[block_index] = block

            if current_piece.status == "complete":
                written = current_piece.write_completed_piece(self.download_filename)
                if written:
                    current_piece.block_data_list = None
                else:
                    current_piece.reset(self.pieces)

    def status(self):
        statuses = [piece.status for piece in self.pieces]
        print '''-*-*-*-*-*-*-*-*-*-*-*-* Checking status -- written: %i, complete: %i, all_requested: %i, semi_requested: %i, unrequested: %i''' % \
                (statuses.count("written"),
                statuses.count("complete"),
                statuses.count("all_requested"),
                statuses.count("semi_requested"),
                statuses.count("unrequested"))
        if all(piece.status == "written" for piece in self.pieces):
            return "complete"
        else:
            return "incomplete"



class Piece(object):
    ''' Contains status of each piece and block of the download, as well as how
        each piece should be requested and written to file. '''

    def __init__(self, index, piece_length, num_request_blocks, total_hash, request_size_list):
        self.index = index
        self.byte_index_in_file = piece_length * index
        self.hash = total_hash[index * 20 : (index * 20) + 20]
        self.num_blocks = num_request_blocks
        self.block_request_status_list = [0] * self.num_blocks
        self.block_request_sizes_list = request_size_list
        self.block_data_list = [''] * self.num_blocks

    def __str__(self):
        return str(self.index) + ": " + self.status + " " + str(self.block_request_status_list)

    @property
    def status(self):
        if self.block_data_list == None:
            return "written"
        elif self.block_data_list.count('') == 0:
            return "complete"
        elif 1 in self.block_request_status_list and 0 in self.block_request_status_list:
            return "semi_requested"
        elif self.block_request_status_list.count(0) == 0:
            return "all_requested"
        else:
            return "unrequested"

    def reset(self, pieces_list):
        ''' Reset piece to 'unrequested' status. '''
        self.block_request_status_list = [0] * self.num_blocks
        self.block_data_list = [''] * self.num_blocks

    def next_unrequested_block_index(self):
        ''' Determine which block should be requested next. '''
        if 0 in self.block_request_status_list:
            return self.block_request_status_list.index(0)
        else:
            return -1

    def write_completed_piece(self, file_name):
        ''' Verifies that the hash of the complete piece matches the corresponding hash
                given in the metainfo file.
            If the hashes match, the piece is written to the correct location in the given file.
            If not, the piece is 'reset' so all blocks will be re-requested. '''
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







