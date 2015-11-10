'''
Created on Nov 10, 2015

@author: Kenny Shu, Wesley Wong
'''

import socket

class rxp(socket.socket):
    _recv_buffer = []
    _send_buffer = []
    
    _header = b''
    
    
    def socket(self):
        pass
    
    def bind(self, address):
        pass
    
    def connect(self, address):
        pass
    
    def listen(self):
        pass
    
    def accept(self):
        pass
    
    def send(self, byte_string):
        pass

    def receive(self, size):
        pass
    
    def close(self):
        pass
    
    def settimeime(self, seconds):
        pass
    
    def gettimeout(self):
        pass


    