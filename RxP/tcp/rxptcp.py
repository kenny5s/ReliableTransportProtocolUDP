'''
Created on Nov 17, 2015

@author: Kenny
'''

import socket

class RxpTcp(object):

    def __init__(self):
        self._sock = socket.socket(type=socket.SOCK_STREAM)
        
    def bind(self, address_tuple):
        return self._sock.bind(address_tuple)
    
    def connect(self, address):
        return self._sock.connect(address)
    
    def listen(self, backlog):
        return self._sock.listen(backlog)
    
    def accept(self):
        return self._sock.accept()
    
    def send(self, bytes):
        return self._sock.send(bytes)

    def receive(self, size):
        return self._sock.recv(size)
    
    def close(self):
        return self._sock.close()
        