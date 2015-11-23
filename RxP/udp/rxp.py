'''
Created on Nov 10, 2015

@author: Kenny Shu, Wesley Wong
'''

import socket
import struct
import collections
import threading
import logging

from enum import Enum

'''
Selective Repeat Protocol
Send and Receive Buffers
Listening for connections
3-way handshake
'''

class States(Enum):
    CLOSED = 0
    LISTEN = 1
    SYN_RCVD = 2
    SYN_SENT = 3
    ESTABLISHED = 4
    FIN_WAIT_1 = 5
    FIN_WAIT_2 = 6
    CLOSING = 7
    TIMED_WAIT = 8
    CLOSE_WAIT = 9
    LAST_ACK = 10
    SYN_ACK_RCVD = 11
    
class Flags(Enum):
    ACK = 1 << 4
    SYN = 1 << 1
    SYN_ACK = ACK + SYN
    RST = 1 << 2
    PSH = 1 << 3
    URG = 1 << 5
    NACK = 1 << 6
    FIN = 1
    FIN_ACK = FIN + ACK

class RxpSocket:

    _send_buffer = bytearray() # bytes (no limit)
    _recv_buffer = bytearray() # bytes
    _recv_buffer_max = 1000000 # 1Mb max (better if multiple of _max_packet_size)
    
    _CLOSING_TIMEOUT = 2 #seconds
    _SENDING_TIMEOUT = 0.003 #seconds
    
    _logger = logging.getLogger(__name__)
    _sock = None
    _lock = threading.Lock()
    _state = None
    _closing_timer = None
    _ctrl_timer = None
    _ctrl_needs_sending = True
    
    _pending_connections = {}
    _established_connections = collections.OrderedDict()
    _accepted_connections = {}
    _max_backlog_connections = 1
    _parent_socket = None
    
    _src = ()
    _dest = ()
    
    
    def __init__(self):
        self._sock = socket.socket(type=socket.SOCK_DGRAM)
        self._sock.setblocking(False)
        self._state = States.CLOSED
        
        def become_closed():
            self._state = States.CLOSED
            if self._parent_socket is None:
                self._sock.close()
            else:
                #remove from parent
                self._parent_socket = None
                
        self._closing_timer = threading.Timer(self._CLOSING_TIMEOUT, become_closed)
        
        def ctrl_timed_out_true():
            self._ctrl_needs_sending = True
        self._ctrl_timer = threading.Timer(self._SENDING_TIMEOUT, ctrl_timed_out_true)
        
    def bind(self, address):
        #can only bind if not connected
        with self._lock:
            self._sock.bind(address)
        self._src = address
        if address[0] in ['localhost', '']:
            self._src[0] = '127.0.0.1'
            
    def listen(self, backlog):
        #can only listen if not bound
        self._max_backlog_connections = backlog
        self._state = States.LISTEN
        
    def accept(self):
        pass
            
    def connect(self, address):
        self._send_ctrl_msg(Flags.SYN, True)
        self._state = States.SYN_SENT
        self._dest = address
        if address[0] in ['localhost', '']:
            self._dest[0] = '127.0.0.1'
        #needs to wait until connected
                    
    def close(self):
        self._send_ctrl_msg(Flags.FIN, True)
        self._state = States.FIN_WAIT_1
        #needs to wait until closed
        
    def _udp_sendto(self, data, address):
        if self._parent_socket is None:
            with self._lock:
                value = self._sock.sendto(data, address)
        else:
            with self._lock:
                value = self._parent_socket._sock.sendto(data, address)
        return value
    
    def _udp_recvfrom(self, buff_size):
        if self._parent_socket is None:
            value = self._sock.recvfrom(buff_size)
        else:
            value = self._parent_socket._
        return value
    
    def _send_ctrl_msg(self, flags, timer=False):
        pkt = RxpPacket()
        pkt.header.flags = flags
        self._sock.sendto(pkt.to_bytes(), self._dest)
        if timer == True:
            self._ctrl_needs_sending = False
            self._ctrl_timer.start()
            
    def _resend_ctrl_msg(self, flags):
        if(self._ctrl_needs_sending):
            self._ctrl_needs_sending = False
            pkt = RxpPacket()
            pkt.header.flags = flags
            self._udp_sendto(pkt.to_bytes(), self._dest)
            self._ctrl_timer.start()

    def send(self, data):
        self._send_buffer.extend(data)
        return len(data)

    def receive(self, buffer_size):
        ret = _recv_buffer[:buffer_size]
        _recv_buffer = _recv_buffer[buffer_size:]
        return ret
        
    def _send_receive_thread(self):
        while(True):
            #Handle Sending
            if self._state == States.CLOSED:
                pass
            
            elif self._state == States.LISTEN:
                pass
            
            elif self._state == States.SYN_RCVD:
                self._resend_ctrl_msg(Flags.SYN_ACK)
                
            elif self._state == States.SYN_SENT:
                self._resend_ctrl_msg(Flags.SYN)
                
            elif self._state == States.SYN_ACK_RCVD:
                self._resend_ctrl_msg(Flags.ACK)
                
            elif self._state == States.ESTABLISHED:
                #Pipeline Send:
                #Does not require a port to be binded
                #Will constantly check the send buffer for packets, pop data out of it into a sending window,
                #send the packet to the target destination, waits for acks or timeout, if timeout resend the packet,
                #else slide the window
                pass
            
            elif self._state == States.FIN_WAIT_1:
                self._resend_ctrl_msg(Flags.FIN)
            
            elif self._state == States.FIN_WAIT_2:
                pass
            
            elif self._state == States.CLOSING:
                self._resend_ctrl_msg(Flags.ACK)
                
            elif self._state == States.TIMED_WAIT:
                self._resend_ctrl_msg(Flags.ACK)
                
            elif self._state == States.CLOSE_WAIT:
                self._resend_ctrl_msg(Flags.ACK)
                
            elif self._state == States.LAST_ACK:
                self._resend_ctrl_msg(Flags.FIN)
            
            #Handle Receiving
            try:
                data, addr = self._sock.recvfrom(self._udp_buffer_size)
            except Exception as e:
                self._logger.debug(e)
                self._logger.debug("Nothing received.")
            else:
                pkt = RxpPacket()
                pkt.from_bytes(data)
                header = pkt.header
                
                if self._state == States.CLOSED:
                    pass
        
                elif self._state == States.LISTEN:
                    #Requires a binded port
                    #Multiplex connections
                    #Server stays on listen
                    #New child socket is added to connection list
                    if (addr not in self._pending_connections and
                        addr not in self._established_connections and
                        addr not in self._accepted_connections and
                        header.flags == Flags.SYN and
                        (len(self._pending_connections) + len(self._established_connections)) < self._max_backlog_connections):
                        child_socket = RxpSocket()
                        child_socket._state = States.SYN_RCVD
                        child_socket._parent_socket = self
                        self._pending_connections[addr] = child_socket
                    elif addr in self._pending_connections:
                        child_socket = self._pending_connections[addr]
                        if child_socket._state == States.SYN_RCVD:
                            if header.flags == Flags.ACK:
                                self._established_connections[addr] = self._pending_connections.pop(addr)
                                child_socket._state = States.ESTABLISHED
                            elif header.flags == Flags.SYN:
                                reply_pkt = RxpPacket()
                                reply_pkt.header.Flags = Flags.SYN_ACK
                                self._sock.sendto(reply_pkt.to_bytes(), addr)
                            elif header.flags == Flags.RST:
                                self._state = States.LISTEN
                            
                    if header.flags == Flags.SYN:
                        num_backlog = len(self._pending_connections) + len(self._established_connections)
                        if (addr not in self._pending_connections and 
                                addr not in self._established_connections and 
                                addr not in self._accepted_connections and
                                num_backlog < self._max_backlog_connections):
                            self._pending_connections[addr] = addr
                        if (addr in self._pending_connections or
                                addr in self._established_connections or
                                addr in self._accepted_connections or 
                                num_backlog < self._max_backlog_connections):
                            self._state = States.SYN_RCVD
                            reply_pkt = RxpPacket()
                            reply_pkt.header.Flags = Flags.SYN_ACK
                            self._sock.sendto(reply_pkt.to_bytes(), addr)
                        
                elif self._state == States.SYN_RCVD:
                    #could only really get here as child socket
                    #merge into listen?
                    if header.flags == Flags.ACK:
                        #maybe handle accept()?
                        self._state = States.ESTABLISHED
                    elif header.flags == Flags.SYN:
                        reply_pkt = RxpPacket()
                        reply_pkt.header.Flags = Flags.SYN_ACK
                        self._sock.sendto(reply_pkt.to_bytes(), addr)
                    elif header.flags == Flags.RST:
                        self._state = States.LISTEN
                        
                elif self._state == States.SYN_SENT:
                    if header.flags == Flags.SYN:
                        self._state = States.SYN_RCVD
                        reply_pkt = RxpPacket()
                        reply_pkt.header.Flags = Flags.SYN_ACK
                        self._sock.sendto(reply_pkt.to_bytes(), addr)
                    elif header.flags == Flags.SYN_ACK:
                        self._state = States.SYN_ACK_RCVD
                        reply_pkt = RxpPacket()
                        reply_pkt.header.Flags = Flags.ACK
                        self._sock.sendto(reply_pkt.to_bytes(), addr)
                        
                elif self._state == States.SYN_ACK_RCVD:
                    if header.flags == Flags.ACK:
                        self._state = States.ESTABLISHED 
                
                elif self._state == States.ESTABLISHED:
                    if header.flags == Flags.FIN:
                        self._state = States.CLOSE_WAIT
                        reply_pkt = RxpPacket()
                        reply_pkt.header.Flags = Flags.ACK
                        self._sock.sendto(reply_pkt.to_bytes(), addr)
                    elif header.flags == Flags.SYN_ACK:
                        reply_pkt = RxpPacket()
                        reply_pkt.header.Flags = Flags.ACK
                        self._sock.sendto(reply_pkt.to_bytes(), addr)
                    elif header.flags == 0:
                        #pipeline receive:
                        #check seq number
                        #if curr_seq is higher and not window, put packet in window_buffer
                        #if all seq numbers up to this one is received, put in recv buffer
                        #ack back w/ recv_window
                        reply_pkt = RxpPacket(b"Hello")
                        self._sock.sendto(reply_pkt.to_bytes(), addr)
                
                elif self._state == States.FIN_WAIT_1:
                    if header.flags == Flags.FIN:
                        self._state = States.CLOSING
                        reply_pkt = RxpPacket()
                        reply_pkt.header.Flags = Flags.ACK
                        self._sock.sendto(reply_pkt.to_bytes(), addr)
                    elif header.flags == Flags.ACK:
                        self._state = States.FIN_WAIT_2
                    elif header.flags == Flags.FIN_ACK:
                        self._state = States.TIMED_WAIT
                        self._closing_timer.start()
                        reply_pkt = RxpPacket()
                        reply_pkt.header.Flags = Flags.ACK
                        self._sock.sendto(reply_pkt.to_bytes(), addr)
                
                elif self._state == States.FIN_WAIT_2:
                    if header.flags == Flags.FIN:
                        self._state = States.TIMED_WAIT
                        self._closing_timer.start()
                        reply_pkt = RxpPacket()
                        reply_pkt.header.Flags = Flags.ACK
                        self._sock.sendto(reply_pkt.to_bytes(), addr)
                        
                elif self._state == States.CLOSING:
                    if header.flags == Flags.ACK:
                        self._state = States.TIMED_WAIT
                        self._closing_timer.start()
                    elif header.flags == Flags.FIN:
                        reply_pkt = RxpPacket()
                        reply_pkt.header.Flags = Flags.ACK
                        self._sock.sendto(reply_pkt.to_bytes(), addr)
            
                elif self._state == States.TIMED_WAIT:
                    if header.flags == Flags.FIN or header.flags == Flags.FIN_ACK:
                        reply_pkt = RxpPacket()
                        reply_pkt.header.Flags = Flags.ACK
                        self._sock.sendto(reply_pkt.to_bytes(), addr)


class RxpSocket_old:
    _send_buffer = bytearray() # bytes (no limit)
    _recv_buffer = bytearray() # bytes
    _recv_buffer_max = 1000000 # 1Mb max (better if multiple of _max_packet_size)
    _udp_buffer_size = 1024
    _max_packet_size = 1024
    _window_send_buffer = [] # tuple: (packet, timer)
    _window_receive_buffer = [] # packets
    _recv_window_size = 2048 # bytes, dynamic (how much more we can  hold)
    _send_window_size = 2048 # bytes, dynamic (how much more they can hold)
    _next_seq = 0
    _next_ack = 0
    
    _parent_socket = None
    _accepted_connections = {}
    _successful_connections = []
    _pending_connections = []
    _connected = False
    _pipeline_enabled = False
    _is_listening = False
    
    _header = b''
    _sock = None
    
    _connect_retries = 3
    _src_ip = ''
    _src_port = None
    _dst_ip = ''
    _dst_port = None
    _seq_number = 0 #seq num in send buffer
    _is_bound = False
    _is_connected = False
    
    def __init__(self):
        self._sock = socket.socket(type=socket.SOCK_DGRAM)
        self._sock.setblocking(False)
        #! TODO
        #startthread: send_thread
        
    def bind(self, address_tuple):
        if not self._is_connected and not self._is_bound:
            _src_ip = address_tuple[0]
            _src_port = address_tuple[1]
            self._sock.bind(address_tuple)
            self._is_bound = True
        elif self._is_connected:
            print("Cannot bind() when connect() has been called.")
        elif self._is_bound:
            print("Cannot bind() when bind() has already been called.")
    
    def connect(self, address):
        if not self._is_bound and not self._is_connected:
            dst_addr = address[0]
            dst_port = address[1]
            if dst_addr in ['localhost', '']:
                dst_addr = '127.0.0.1'
            attempts = 0
            self._sock.settimeout(3)
            while(not self._is_connected or attempts <= self._connect_retries):
                try:
                    #send SYN
                    pkt = RxpPacket()
                    pkt.header.syn = 1
                    pkt.header.window_size = self._get_recv_win_size()
                    self._sock.sendto(pkt.to_bytes(),(dst_addr, dst_port))
                    
                    #wait for ACK
                    addr = None
                    while(addr != (dst_addr, dst_port)):
                        reply, addr = self._sock.recvfrom(1024)
                    pkt = RxpPacket()
                    pkt.from_bytes(reply)
                    
                    #if ACK
                    if pkt.header.ack == 1 and pkt.header.syn == 0:
                        
                        #send SYN-ACK
                        pkt = RxpPacket()
                        pkt.header.syn = 1
                        pkt.header.ack = 1
                        pkt.header.window_size = self._get_recv_win_size()
                        self._sock.sendto(pkt.to_bytes(),(dst_addr, dst_port))
                        
                        #wait for ACK
                        addr = None
                        while(addr != (dst_addr, dst_port)):
                            reply, addr = self._sock.recvfrom(1024)
                        pkt = RxpPacket()
                        pkt.from_bytes(reply)
                        
                        #if ACK
                        if pkt.header.ack == 1 and pkt.header.syn == 0:
                            self._is_connected = True
                            self._dst_ip = dst_addr
                            self._dst_port = dst_port
                    
                except socket.timeout:
                    print("DEBUG: timed out")
                    pass
                attempts += 1
            self._is_connected = True
        elif self._is_bound:
            print("Cannot connect() when bind() has been called.")
        elif self._is_connected:
            print("Cannot call connect() when connect() has already been called.")
        self._sock.setblocking(False)
            
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
            
    '''
    Will constantly receive packets into window_recv_buffer, send acks for packets received, checks packet headers for additional actions,
    SYN-ACK handshake, unwrap acked packets and push into recv buffer
    '''
    def _recv_thread(self):
        while(True):
            data, addr = self._sock.recvfrom(self._udp_buffer_size)
            pkt = RxpPacket()
            if addr == (self._dst_ip,self._dst_port):
                self._send_window_size = pkt.header.window_size
                #check sequence number
                pass
            elif addr not in self._connection_queue:
                pass
    
    #NOT NEEDED?        
    def _listen_thread(self, backlog):
        self._sock.recvfrom(self._udp_buffer_size)
        
    def _populate_header(self, packet):
        packet.header.seq_number = self._next_seq
        packet.header.ack_number = self._next_ack
        self._next_seq += len(packet.payload)
        #self._next_ack += 
        
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
        '''
        header = RxpHeader()
        header.src_port = self._src_port
        header.dest_port = self._dst_port
        header.seq_number = self._seq_number
        header.ack_number = 0
        header.window_size = self._get_recv_win_size()
        '''
        self._send_buffer.extend(data_bytes)
        
    def _recv_wait_from(self, addr, buff_size, blocking=True):
        self._sock.setblocking(True)
        dst = None
        while(dst != addr):
            reply, dst = self._sock.recvfrom(buff_size)
        reply_pkt = RxpPacket()
        return reply_pkt.from_bytes(reply)
    
    #Starts a new thread to receive a syn request
    def listen(self, backlog):
        self._is_listening = True
        #start thread: _recv_thread
    
    def accept(self):
        if self._is_bound and self._is_listening:
            while(not self._successful_connections):
                #wait for a successful connection
                pass
            else:
                connection = self._successful_connections.pop(False)
                child_sock = RxpSocket()
                child_sock._parent_socket = self
                child_sock._is_connected = True
                self._accepted_connections[connection] = child_sock
                return child_sock
        else:
            print("Can only accept() when bind() and listen() has been called.")
    
    def send(self, bytes):
        self._send_data_to((self._dst_ip,self._dst_port), bytes)

    def receive(self, size):
        value = self._recv_buffer[:size]
        self._recv_buffer = self._recv_buffer[size:]
        return value
    
    def close(self):
        if self._is_connected:
            pkt = RxpPacket()
            pkt.header.fin = 1
            pkt.header.window_size = self._get_recv_win_size()
            dest = (self._dst_ip, self._dst_port)
            
            fin_received = False
            while(not fin_received):
                #send FIN
                self._sock.sendto(pkt.to_bytes(),dest)
                #wait for ACK or FIN or FIN+ACK (FIN-WAIT-1)
                reply_pkt = self._recv_wait_from(dest, 1024)
                
                #if receive FIN+ACK
                if reply_pkt.header.fin == 1 and reply_pkt.header.ack == 1:
                    ack_received = False
                    while(not ack_received):
                        #send ACK (TIMED-WAIT)
                        self._sock.sendto(pkt.to_bytes(), dest)
                        #wait for 
                        addr = None
                        while(addr != dest):
                            reply, addr = self._sock.recvfrom(1024)
                        reply_pkt = RxpPacket()
                        reply_pkt.from_bytes(reply)
                    
                
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
    
    
    def get_flags(self):
        return (self.nack << 6) + (self.urg << 5) + (self.ack << 4) + (self.psh << 3) + (self.rst << 2) + (self.syn << 1) + self.fin

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

    def set_flags(self, value):
        nack_mask = 1 << 6
        urg_mask = 1 << 5
        ack_mask = 1 << 4
        psh_mask = 1 << 3
        rst_mask = 1 << 2
        syn_mask = 1 << 1
        fin_mask = 1
        self.nack = (value & nack_mask) >> 6
        self.urg = (value & urg_mask) >> 5
        self.ack = (value & ack_mask) >> 4
        self.psh = (value & psh_mask) >> 3
        self.rst = (value & rst_mask) >> 2
        self.syn = (value & syn_mask) >> 1
        self.fin = value & fin_mask

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
    flags = property(get_flags, set_flags)
    
    