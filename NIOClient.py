import socket
import sys
import struct
from messages.client.CM_TEST import CM_TEST
from messages.client.CM_PING import CM_PING
from dyn_class.test import Pong
import time
import datetime

def read(sock):
    data = sock.recv(1024)
        
def write(sock, msg):
    data = msg.get_data()
    opcode = type(msg).OP_CODE
    #print(opcode)
    length = len(data)
    #print(length)
    #print(data)
    
    buffer = bytearray()
    buffer.extend(struct.pack('<I', length))
    buffer.extend(struct.pack('<B', opcode))
    buffer.extend(data)
    
    buffer.extend(struct.pack('<I', length))
    buffer.extend(struct.pack('<B', opcode))
    buffer.extend(data)
    
    buffer.extend(struct.pack('<I', length))
    buffer.extend(struct.pack('<B', opcode))
    buffer.extend(data)
    
    buffer.extend(struct.pack('<I', length))
    buffer.extend(struct.pack('<B', opcode))
    buffer.extend(data)    
    
    sock.send(buffer)
    
if __name__ == '__main__':
    #cmessage = CM_TEST(33, True, 1234567890, 22, 3.5, 310.55, 'Jadrejčić', -1, Pong('You pinged?'))
    cmessage = CM_PING("a"*32)
    
    server_address = ('localhost', 10000)
    
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
              #]
    
    # Connect the socket to the port where the server is listening
    print('connecting to %s'.format(server_address))    
    sock.connect(server_address)
    
    
    for x in range(0,200):
        st = datetime.datetime.now()    
        write(sock, cmessage)
        read(sock)
        end = datetime.datetime.now()
        print('Ping {0} ms'.format((end-st).microseconds/1000))
     
    sock.close()        
