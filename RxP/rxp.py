'''
Created on Nov 10, 2015

@author: Kenny Shu, Wesley Wong
'''

import socket
import struct

'''
Selective Repeat Protocol
Send and Receive Buffers
Listening for connections
3-way handshake
'''

class Rxp:
    _recv_buffer = []
    _send_buffer = []
    
    _src_ip = ''
    _dest_ip = ''
    _src_port = 0
    _dest_port = 0
    _seq_number = 0
    _ack_number = 0
    _data_offset = 0
    _reserved = 0
    _nack = 0
    _urg = 0
    _ack = 0
    _psh = 0
    _rst = 0
    _syn = 0
    _fin = 0
    _window_size = 0
    _checksum = 0
    _urgent_pointer = 0
    _options = 0
    _payload = b''
    
    _header = b''
    _sock = None
    
    _connect_retries = 1
    
    def __init__(self):
        self._sock = socket.socket(type=socket.SOCK_DGRAM)
        
    def bind(self, address_tuple):
        _src_ip = address_tuple[0]
        _src_port = address_tuple[1]
        self._sock.bind(address_tuple)
    
    def connect(self, address):
        attempts = 0
        while(attempts <= self._connect_retries):
            self.send(self.generate_header())
    
    def listen(self):
        pass
    
    def accept(self):
        pass
    
    def send(self, byte_string):
        pkt = RxpPacket(byte_string)
        pass

    def receive(self, size):
        pass
    
    def close(self):
        self._sock.close()
        pass
    
    def set_timeout(self, seconds):
        pass
    
    def get_timeout(self):
        pass

    def generate_header(self, src=0, dst=0, seq=0, ack_num=0, dat_off=0,resrv=0,nck=0,urg=0,ack=0,psh=0,rst=0,syn=0,fin=0,win_size=0,chksum=0,urgptr=0,opts=0,data=b''):
        pass
    
    def send_ack(self):
        self.send(self.generate_header())
      
      
class RxpPacket:
    def __init__(self):
        self.header = RxpHeader()
        
class RxpHeader:
    _src_port = 0
    _dest_port = 0
    _seq_number = 0
    _ack_number = 0
    _data_offset = 0
    _reserved = 0
    _nack = 0
    _urg = 0
    _ack = 0
    _psh = 0
    _rst = 0
    _syn = 0
    _fin = 0
    _window_size = 0
    _checksum = 0
    _urgent_pointer = 0
    _options = 0
    _payload = b''
    
    def __init__(self):
        pass

    def set_source_port(self, src):
        self._src_port = src
    