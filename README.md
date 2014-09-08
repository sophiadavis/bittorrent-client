### BitTorrent Client
  
-----------  
Sophia Davis  
Summer 2014  

----------

This program uses [UDP protocol](http://www.rasterbar.com/products/libtorrent/udp_tracker_protocol.html) to connect to one tracker and download files from other peers connected to that tracker. Both single and multi-file torrents are supported. 

I approached this project as suggested by [Kristin Widman](http://www.kristenwidman.com/blog/how-to-write-a-bittorrent-client-part-1/) in her awesome blog post. For more information, the [spec](http://www.bittorrent.org/beps/bep_0003.html) is very useful, as is the [unofficial wiki spec](https://wiki.theory.org/BitTorrentSpecification).    

Functions for the initial processing of metainfo files (bencoding, length calculation, etc.) was heavily tested. After that I mostly relied on direct interaction with the tracker and peers.

## Usage

```
python session.py metainfo_file.torrent Download/Path
```
