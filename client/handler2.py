from common.connection import Connection
from common.log_optional import Logger
from common.input_output import read, write, add_messages_to_write_buffer
import queue
import select
import socket
from multiprocessing.reduction import rebuild_handle 

def run(idx, handle, read_queue, write_queue, debug):    
    logger=Logger(debug)    
        
    logger.log("Start handler {0}".format(idx))
    
    inputs = []
    outputs=[]
    
    fd=rebuild_handle(handle)
    client=socket.fromfd(fd,socket.AF_INET,socket.SOCK_STREAM)   
    connection = Connection(client)
    
    try:
        while True:         
            try:
                messages = write_queue.get(False)                
            except queue.Empty:
                pass
            else:
                if len(messages)>0:
                    logger.log('Handler {0}: add {1} messages to write buffer'.format(idx, messages))
                for message in messages:
                    add_messages_to_write_buffer(idx, connection, message, logger) 
                
                #if we have message to sent to server, add to outputs
                if not client in outputs:
                    logger.log('Handler {0}: add client {1} to write select list'.format(idx, client))
                    outputs.append(client) 
                
                if client in inputs:
                    inputs.remove(client)
    
            #logger.log('Handler {0}: inputs={1}, outputs={2}'.format(idx, len(inputs), len(outputs)))
            
            readable,writable,exceptional = select.select(inputs, outputs, inputs)
            
            #logger.log('Handler {0}: readable {1}, writable {2}, exceptions {3}'.format(idx, len(readable), len(writable), len(exceptional)))
            
            read_messages=[]
            
            for client in readable:                        
                try:
                    logger.log('Handler {0} read data from client {1}'.format(idx, client.getpeername()))
                    messages = read(idx, connection, logger)
                    logger.log('Handler {0}: processed {1} messages'.format(idx, len(messages)))
                    #if we got some messages we want to write to server, and stop reading
                    if len(messages)>0:
                        for message in messages:
                            read_messages.append(message)
                        if not client in outputs:
                            outputs.append(client)
                               
                    logger.log('Handler {0}: exit read for client {1}'.format(idx, client.getpeername()))
                except socket.error as error:
                    logger.log(repr(error))
                    if client in outputs:               
                        outputs.remove(client)                
                    if client in inputs:                                    
                        inputs.remove(client)                     
                    return
                except ValueError as error:
                    logger.log('Handler {0}: client {1} disconnected'.format(idx, client.getpeername()))
                    if client in outputs:               
                        outputs.remove(client)                
                    if client in inputs:                                    
                        inputs.remove(client)                
                    client.close()  
                    return
            
            if len(read_messages)>0:
                read_queue.put(read_messages)
           
            for client in writable:
                try:             
                    if client==connection.connection and len(connection.write_buffer)>0:
                        logger.log('Handler {0} write data to client {1}'.format(idx, client.getpeername()))                    
                        write(idx, connection, logger) 
                        if len(connection.write_buffer)==0:
                            logger.log('Handler {0}: write buffer for client {1} is empty'.format(idx, client))
                            #if buffer is empty go to reading
                            if client in outputs:                            
                                outputs.remove(client)                             
                            #if we wrote whole buffer begin reading  
                            if not client in inputs:                                    
                                inputs.append(client)                                                        
                except socket.error as error:
                    logger.log(repr(error))
                    if client in outputs:               
                        outputs.remove(client)                
                    if client in inputs:                                    
                        inputs.remove(client)                     
                    return
                except ValueError as error:
                    logger.log('Handler {0}: client {1} disconnected'.format(idx, client.getpeername()))
                    if client in outputs:                
                        outputs.remove(client)
                    if client in inputs:                                    
                        inputs.remove(client)
                    client.close()
                    return
    
            # Handle "exceptional conditions"
            for client in exceptional:
                logger.log('Handling exceptional condition for'.format(client.getpeername()))
                # Stop listening for input on the connection
                inputs.remove(client)            
                outputs.remove(client)
                client.close()
    except Exception as ex:
        logger.log('Handler {0}: exception: {1}'.format(idx, ex))       
    