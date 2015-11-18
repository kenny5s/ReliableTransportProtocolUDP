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
    
    _header = b''
    _sock = None
    
    _connect_retries = 3
    _dst_address = ''
    _dst_port = None
    
    def __init__(self):
        self._sock = socket.socket(type=socket.SOCK_DGRAM)
        
    def bind(self, address_tuple):
        _src_ip = address_tuple[0]
        _src_port = address_tuple[1]
        self._sock.bind(address_tuple)
    
    def connect(self, address):
        dst_addr = address[0]
        dst_port = address[1]
        attempts = 0
        while(attempts <= self._connect_retries):
            try:
                pkt = RxpPacket()
                pkt.header.syn = 1
                self._send_to(dst_addr, dst_port, pkt)
            except:
                pass
    
    def listen(self, backlog):
        pass
    
    def accept(self):
        pass
    
    def _send_to(self, address, port, rxp_packet):
        return self._sock.sendall(rxp_packet.to_bytes())
    
    def send(self, byte_string):
        pkt = RxpPacket(byte_string)
        self._send_to(self._dst_address, self._dst_port, pkt)

    def receive(self, size):
        pass
    
    def close(self):
        self._sock.close()
        pass
    
    def set_timeout(self, seconds):
        pass
    
    def get_timeout(self):
        pass
    
    def send_ack(self):
        self.send(self.generate_header())
      
      
class RxpPacket:
    
    def __init__(self, data_bytes=None):
        self.header = RxpHeader()
        self.payload = b'' if data_bytes is None else data_bytes 
    
    def to_bytes(self):
        self.header.to_bytes() + bytearray(self.payload)
        
class RxpHeader:
    HEADER_FORMAT = '!HHLLHHHH'
    
    def __init__(self):
        self.src_port = 0           #16 bits = 2 bytes = H
        self.dest_port = 0          #16 bits = 2 bytes = H
        self.seq_number = 0         #32 bits = 4 bytes = L
        self.ack_number = 0         #32 bits = 4 bytes = L
        self.data_offset = 0        #4 bits
        self.reserved = 0           #5 bits
        self.nack = 0               #1 bit
        self.urg = 0                #1 bit
        self.ack = 0                #1 bit
        self.psh = 0                #1 bit
        self.rst = 0                #1 bit
        self.syn = 0                #1 bit
        self.fin = 0                #1 bit
        self.window_size = 0        #16 bits = 2 bytes = H
        self.checksum = 0           #16 bits = 2 bytes = H
        self.urgent_pointer = 0     #16 bits = 2 bytes = H

    def get_src_port(self):
        return self.__src_port


    def get_dest_port(self):
        return self.__dest_port


    def get_seq_number(self):
        return self.__seq_number


    def get_ack_number(self):
        return self.__ack_number


    def get_data_offset(self):
        return self.__data_offset


    def get_reserved(self):
        return self.__reserved


    def get_nack(self):
        return self.__nack


    def get_urg(self):
        return self.__urg


    def get_ack(self):
        return self.__ack


    def get_psh(self):
        return self.__psh


    def get_rst(self):
        return self.__rst


    def get_syn(self):
        return self.__syn


    def get_fin(self):
        return self.__fin


    def get_window_size(self):
        return self.__window_size


    def get_checksum(self):
        return self.__checksum


    def get_urgent_pointer(self):
        return self.__urgent_pointer


    def set_src_port(self, value):
        self.__src_port = value


    def set_dest_port(self, value):
        self.__dest_port = value


    def set_seq_number(self, value):
        self.__seq_number = value


    def set_ack_number(self, value):
        self.__ack_number = value


    def set_data_offset(self, value):
        self.__data_offset = value


    def set_reserved(self, value):
        self.__reserved = value


    def set_nack(self, value):
        self.__nack = value


    def set_urg(self, value):
        self.__urg = value


    def set_ack(self, value):
        self.__ack = value


    def set_psh(self, value):
        self.__psh = value


    def set_rst(self, value):
        self.__rst = value


    def set_syn(self, value):
        self.__syn = value


    def set_fin(self, value):
        self.__fin = value


    def set_window_size(self, value):
        self.__window_size = value


    def set_checksum(self, value):
        self.__checksum = value


    def set_urgent_pointer(self, value):
        self.__urgent_pointer = value
        
    def _pack_octet_12(self):
        packed = (self.data_offset << 12) + (self.reserved << 7) + (self.nack << 6) + (self.urg << 5) + (self.ack << 4) + (self.psh << 3) + (self.rst << 2) + (self.syn << 1) + self.fin 
        return packed
        
    def to_bytes(self):
        octet_12 = self._pack_octet_12()
        return struct.pack(self.HEADER_FORMAT, self.src_port, self.dest_port,
                    self.seq_number, self.ack_number, octet_12,
                    self.window_size, self.checksum, self.urgent_pointer)
    
    src_port = property(get_src_port, set_src_port)
    dest_port = property(get_dest_port, set_dest_port)
    seq_number = property(get_seq_number, set_seq_number)
    ack_number = property(get_ack_number, set_ack_number)
    data_offset = property(get_data_offset, set_data_offset)
    reserved = property(get_reserved, set_reserved)
    nack = property(get_nack, set_nack)
    urg = property(get_urg, set_urg)
    ack = property(get_ack, set_ack)
    psh = property(get_psh, set_psh)
    rst = property(get_rst, set_rst)
    syn = property(get_syn, set_syn)
    fin = property(get_fin, set_fin)
    window_size = property(get_window_size, set_window_size)
    checksum = property(get_checksum, set_checksum)
    urgent_pointer = property(get_urgent_pointer, set_urgent_pointer)
    
    