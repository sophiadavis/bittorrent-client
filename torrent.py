import metainfo

class Torrent(object):
    
    def __init__(self, meta, download_filename):
        self.meta = meta
        self.pieces_status_dict = self._create_pieces_dict()
        self.download_filename = download_filename
        self.next_request = [0, 0] # piece_index, begin
    
    def strategically_get_next_piece_index_and_offset(self):
        # When all blocks for a piece have been received, you should 
        # perform a hash check to verify that the piece matches what is 
        # expected and you have not been sent bad or malicious data.
        return [0, 0]
        
    def _create_pieces_dict(self):
        d = {}
        for piece_index in self.meta.length_dict.keys():
            d[piece_index] = [0, 0, self.meta.length_dict[piece_index]] # last_begin_requested, bytes downloaded, bytes total
        return d
        
    