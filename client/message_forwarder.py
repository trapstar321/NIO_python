import queue

from client.messages.SM_PONG import SM_PONG
from client.messages.CM_PING import CM_PING
from common.log_optional import Logger

import datetime
import socket 
s = None
e = None

def forward_messages(udp_port, read_queue, write_queue, process_messages, debug, pings):
    global s
    global e
    
    logger = Logger(debug)
     
    while True:
        try:
            messages = read_queue.get()                        
        except queue.Empty:
            pass
        else:            
            try:    
                if len(messages)==1 and messages[0]=={}:
                    logger.log('Exit forwarder')
                    return
                                            
                processed_messages = []
                for message in messages:
                    msg = CM_PING("a"*32)
                    processed_messages.append({"opcode":type(msg).OP_CODE, "data":msg.get_data()})
                write_queue.put(processed_messages)
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b'1', ('127.0.0.1', udp_port))
                
                if s:
                    e = datetime.datetime.now()
                    pings.put((e-s).microseconds/1000)          
            except Exception as ex:
                logger.log("forward_messages: exception: {0}".format(ex))
            s = datetime.datetime.now()
  