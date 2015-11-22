'''
Created on Nov 10, 2015

@author: Kenny Shu, Wesley Wong
'''

import socket
import struct
import collections
import threading

'''
Selective Repeat Protocol
Send and Receive Buffers
Listening for connections
3-way handshake
'''

class RxpSocket:
    _send_buffer = [] # packets (no limit)
    _recv_buffer = bytearray() # bytes
    _recv_buffer_max = 1024000 # 1Mb max (this better be a multiple of _max_packet_size)
    _udp_buffer_size = 1024
    _max_packet_size = 1024
    _window_send_buffer = [] # tuple: (packet, timer)
    _window_receive_buffer = [] #packets
    _recv_window_size = 2048 # bytes, dynamic (how much more we can hold)
    _send_window_size = 2048 # bytes, dynamic (how much more they can hold)
    
    _parent_socket = None
    _accepted_connections = {}
    _successful_connections = []
    _pending_connections = []
    _current_connection = None
    _connected = False
    _pipeline_enabled = False
    _listening = False
    
    _header = b''
    _sock = None
    
    _connect_retries = 3
    _src_ip = ''
    _src_port = None
    _dst_ip = ''
    _dst_port = None
    _seq_number = 0 #seq num in send buffer
    
    def __init__(self):
        self._sock = socket.socket(type=socket.SOCK_DGRAM)
        self._sock.setblocking(False)
        #! TODO
        #startthread: send_thread
        
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
            
    def _start_send_thread(self):
        pass
    
    def _start_receive_thread(self):
        pass
            
    '''
    Will constantly check the send buffer for packets, pop data out of it into a sending window,
    send the packet to the target destination, waits for acks or timeout, if timeout resend the packet,
    else slide the window
    '''
    def _send_thread(self, conn):
        while(True):
            if (self._send_buffer) and (len(self._window_send_buffer) < self._send_window_size/self._max_packet_size):
                self._window_send_buffer.append(self._send_buffer.pop(False)) #False = pop from front
            if self._send_window_size < self._max_packet_size:
                pass
            
    '''
    Will constantly receive packets into window_recv_buffer, send acks for packets received, checks packet headers for additional actions,
    SYN-ACK handshake, unwrap acked packets and push into recv buffer
    '''
    def _recv_thread(self):
        while(True):
            data, addr = self._sock.recvfrom(self._udp_buffer_size)
            pkt = RxpPacket()
            if addr == self._current_connection:
                self._send_window_size = pkt.header.window_size
                #check sequence number
                pass
            elif addr not in self._connection_queue:
                pass
    
    #NOT NEEDED?        
    def _listen_thread(self, backlog):
        self._sock.recvfrom(self._udp_buffer_size)
        
    #Splits data into _max_packet_size sized packets with headers and sequence numbers    
    def _packetize(self, data_bytes, header):
        num_packets = (len(data_bytes) + self._max_packet_size)/self._max_packet_size
        packets = []
        next_seq = header.seq_number
        for i in range(num_packets):
            data = data_bytes[:self._max_packet_size*i]
            header.seq_number = next_seq
            pkt = RxpPacket(data, header)
            pkt.header.checksum = self._generate_checksum(pkt)
            packets.append(pkt)
            data_bytes = data_bytes[self._max_packet_size*i:]
            next_seq += len(data)
        if not data_bytes:
            next_seq += 1
        return packets, next_seq
    
    #Takes all of the data in the lists of packets and joins them together
    def _depacketize(self, packets):
        if not isinstance(packets, list):
            packets = [packets]
        data_bytes = b''
        for pkt in packets:
            data_bytes += pkt.payload
        return data_bytes
    
    def _get_recv_win_size(self):
        return self._recv_buffer_max - len(self._recv_buffer)
    
    def _generate_checksum(self, packet):
        #! TODO
        pass
        
    def _send_data_to(self, addr, data_bytes):
        header = RxpHeader()
        header.src_port = self._src_port
        header.dest_port = self._dst_port
        header.seq_number = self._seq_number
        header.ack_number = 0
        header.window_size = self._get_recv_win_size()
        self._send_buffer.append(self._packetize(data_bytes))
    
    #Starts a new thread to receive a syn request
    def listen(self, backlog):
        self._listening = True
        #start thread: _recv_thread
    
    def accept(self):
        while(not self._successful_connections):
            #wait for a successful connection
            pass
        else:
            connection = self._successful_connections.pop(False)
            child_sock = RxpSocket()
            child_sock._parent_socket = self
            self._accepted_connections[connection] = child_sock
            return child_sock
    
    def send(self, bytes):
        self._send_data_to((self._dst_ip,self._dst_port), bytes)

    def receive(self, size):
        value = self._recv_buffer[:size]
        self._recv_buffer = self._recv_buffer[size:]
        return value
    
    def close(self):
        self._sock.close()
        #! TODO
        pass
    
    def set_timeout(self, seconds):
        #! TODO
        pass
    
    def get_timeout(self):
        #! TODO
        pass
    
    def send_ack(self):
        self.send(self.generate_header())
      
      
class RxpPacket:
    
    _header_size = 160 #bits
    
    def __init__(self, data_bytes=None, header=None):
        self.header = RxpHeader() if header is None else header
        self.payload = b'' if data_bytes is None else data_bytes 
    
    def to_bytes(self):
        self.header.to_bytes() + bytearray(self.payload)
        
    def from_bytes(self, packet_bytes):
        data_length = (len(packet_bytes)*8 - self._header_size)
        data_mask = (1 << data_length) - 1
        self.payload = packet_bytes & data_mask
        self.header.from_bytes(packet_bytes >> data_length)
        
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
    
    def _unpack_octet_12(self, packed):
        # packed = aaaabbbbbcdefghi
        offset_mask = 15 << 12 #1111000000000000
        reserved_mask = 31 << 7
        nack_mask = 1 << 6
        urg_mask = 1 << 5
        ack_mask = 1 << 4
        psh_mask = 1 << 3
        rst_mask = 1 << 2
        syn_mask = 1 << 1
        fin_mask = 1
        self.data_offset = (packed & offset_mask) >> 12 
        self.reserved = (packed & reserved_mask) >> 7
        self.nack = (packed & nack_mask) >> 6
        self.urg = (packed & urg_mask) >> 5
        self.ack = (packed & ack_mask) >> 4
        self.psh = (packed & psh_mask) >> 3
        self.rst = (packed & rst_mask) >> 2
        self.syn = (packed & syn_mask) >> 1
        self.fin = packed & fin_mask
        
    def to_bytes(self):
        octet_12 = self._pack_octet_12()
        return struct.pack(self.HEADER_FORMAT, self.src_port, self.dest_port,
                    self.seq_number, self.ack_number, octet_12,
                    self.window_size, self.checksum, self.urgent_pointer)
        
    def from_bytes(self, packed_bytes):
        self.src_port, self.dest_port, self.seq_number, self.ack_number, octet_12, self.window_size, self.checksum, self.urgent_pointer = struct.unpack(self.HEADER_FORMAT, packed_bytes)
        self._unpack_octet_12(octet_12)
        
    
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
    
    