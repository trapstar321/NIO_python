import select
import socket
from multiprocessing.reduction import rebuild_handle
from multiprocessing.reduction import reduce_handle 
from common.log_optional import Logger 

lastHandler = -1

def get_handler(nHandlers):
    global lastHandler                
    if lastHandler==nHandlers-1:            
        lastHandler=0;
    else:        
        lastHandler+=1;
    return lastHandler; 

def accept(h, udp_port, client_queue, nHandlers, debug):    
    try:
        logger=Logger(debug) 
            
        fd=rebuild_handle(h)
        server=socket.fromfd(fd,socket.AF_INET,socket.SOCK_STREAM)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', udp_port))        
        
        inputs = [server, sock]        
        
        while inputs:
            #print('Waiting for next client')        
            readable,writable,exceptional = select.select(inputs, [],[])            
    
            for s in readable:
                if s is server:
                    connection, client_address = s.accept()
                    connection.setblocking(0) 
                    logger.log('accept: new connection from {0}'.format(client_address))                                      
                    
                    
                    handler = get_handler(nHandlers)                
                    logger.log('accept: last handler={0}'.format(handler))
                    
                    logger.log('accept: add connection {0} to handler {1}'.format(client_address, handler))
                    
                    h = reduce_handle(connection.fileno())                 
                    
                    client_queue[handler].put(h)
                    #connection.close()
                elif s is sock:
                    s.recvfrom(8)
                    logger.log('accept: exit')
                    return                                   
                else:
                    logger.log('accept: select returned {0}'.format(s))  
    except Exception as ex:
        print(ex)    