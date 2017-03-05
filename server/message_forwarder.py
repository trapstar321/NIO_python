import queue
import socket
from server.messages.SM_PONG import SM_PONG
from common.log_optional import Logger

def forward_messages(udp_port, read_queue, write_queue, process_messages, debug):
    global sent
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
                    msg = SM_PONG("a"*32)
                    processed_messages.append({"id":message["id"],"opcode":type(msg).OP_CODE, "data":msg.get_data()})                
                write_queue.put(processed_messages)                
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b'1', ('127.0.0.1', udp_port))
            except Exception as ex:
                print('forward_messages: exception: {0}'.format(ex))
        
        