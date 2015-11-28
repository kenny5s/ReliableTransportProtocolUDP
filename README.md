Name: Kenny Shu, Wesley Wong
E-mail: kshu6@gatech.edu ,wwong30@gatech.edu
Sockets programming assignment 2

# ReliableTransportProtocolUDP

Python version: 3.4.3

Instructions on running the program:
	-After obtaining python 3.4.3, open command line and cd to the file directory
	-To run the client, type in 'FxA.py [client_port] [netemu_addr] [netemu_port]' 
	-Similarly, to run server, type in 'FxA_Server.py [server_port] [netemu_addr] [netemu_port]'
	- '-h' (help) option available
	- '-d' (debugging) is also available


Python Reliable Transport Protocol over UDP, along with a File Transport Application

Our RxP is modeled after the TCP protocol

functions:
_send_receive_thred(self):
This function tracks what state the socket is on and sends appropriate flags for send, receive, and close. This function is the direct reproduction of the TCP's state diagram. 

recv(self, buffer_size):
Slices at most buffer_size bytes off of the receive buffer, then returns the buffer size in bytes

sendall(self, data):
Puts the data into the  send buffer, does not return anything

send(self, data):
Puts the data into the send buffer, returns the len(data)

_generate_checksum(self, packet):
Takes in bytearray. Bytearray contains all header data and payload data in bytes. Calculates the one's compliment of the one's compliment sum. Uses _carry_around_add function to add the carries back instead of carrying to the next bit. NOTE: assumes checksum value 0 when calculating

_validate_checksum(self, packet):
Returns true if the checksum received is equal to the checksum calculated.

_send_ctrl_msg(self, flags, addr, timer=False):
Used to send control message, a.k.a the flags. 

_udp_recvfrom(self, buff_size):



File Transport App

Client takes in 5 commands: connect, get, post, window, disconnect.
Connect - connects to the file transfer server, this must be called first before doing anything
Post - Basically uploads the file to the server, must specify the file. If file not in current directory, the directory must be specified. The file extension must also be present in the name. If file does not exist, the application will let you know
Get - Basically downloads the file to the server, must specify the file. If file does not exist, the application will let you know
Window - Changes the window size
Disconnect - Disconnects from the server and ends the application

File transfer protocol:
-Get: The client first send "GET" command to the server, so the server knows which command to process. Next client sends the file name with the extension, so server knows what type of file to create and what to name it. Client then calculates the file size so server knows when to stop receiving. Finally it sends the file binaries to the server.
-Post: The client first send "POST" command to the server, so the server knows which command to process. Next client sends the file name with the extension, so server knows what type of file to send to server. Server then calculates the file size so client knows when to stop receiving. Finally Server sends the file binaries to the client.
-Connect: Simple conect to the server
-Disconnect: Disconnect to the server and close the application


