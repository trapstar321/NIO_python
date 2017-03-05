from common.connection import Connection
from common.log_optional import Logger
from common.input_output import read, write, add_messages_to_write_buffer
import queue
import select
import socket
from multiprocessing.reduction import rebuild_handle 

def run(idx, client_queue, read_queue, write_queue, debug):    
    logger=Logger(debug)    
        
    logger.log("Start handler {0}".format(idx))
    
    inputs = []
    outputs=[]    
    server_connections = {}   
    connection_ids = {} 
    
    try:
        while True:            
            try:                           
                if len(server_connections)==0:
                    h = client_queue.get()
                else:            
                    h = client_queue.get(False)
            except queue.Empty:
                pass
            except Exception as ex:
                logger.log(ex) 
            else:  
                fd=rebuild_handle(h)
                client=socket.fromfd(fd,socket.AF_INET,socket.SOCK_STREAM)
                logger.log('Handler {0} got new client {1}'.format(idx, client.getpeername()))                   
                inputs.append(client)
                sc = Connection(client)
                server_connections[client]=sc     
                connection_ids[sc.id]=sc                                       
               
            try:                
                messages = write_queue.get(False)            
            except queue.Empty:
                pass
            else:
                if len(messages)>0:
                    logger.log('Handler {0}: add {1} messages to write buffer'.format(idx, messages))
                for message in messages:
                    connection = connection_ids[message["id"]]
                    add_messages_to_write_buffer(idx, connection, message, logger) 
                
                    #if we have message to sent to server, add to outputs
                    if not connection.connection in outputs:
                        logger.log('Handler {0}: add client {1} to write select list'.format(idx, connection.connection))
                        outputs.append(client) 
                    
                    if connection.connection in inputs:
                        inputs.remove(connection.connection)       
    
            if not inputs and not outputs:            
                continue
            
            #logger.log('Handler {0}: inputs={1}, outputs={2}'.format(idx, len(inputs), len(outputs)))
            
            readable,writable,exceptional = select.select(inputs, outputs, inputs)
            
            #logger.log('Handler {0}: readable {1}, writable {2}, exceptions {3}'.format(idx, len(readable), len(writable), len(exceptional)))
    
            read_messages = []
    
            for client in readable:                        
                try:
                    logger.log('Handler {0} read data from client {1}'.format(idx, client.getpeername()))
                    messages = read(idx, server_connections[client], logger)                                
                    logger.log('Handler {0}: processed {1} messages'.format(idx, len(messages)))
                    
                    #add ID for client in message dictionary                
                    for message in messages:                    
                        message["id"]=server_connections[client].id                   
                    
                    if len(messages)>0:               
                        for message in messages:     
                            read_messages.append(message)                        
                        if not client in outputs:
                            outputs.append(client)
                               
                    logger.log('Handler {0}: exit read for client {1}'.format(idx, client.getpeername()))
                except socket.error as error:
                    logger.log("Handler {0}: {1}".format(idx, repr(error)))
                    if client in inputs: 
                        inputs.remove(client)    
                    if client in outputs:  
                        outputs.remove(client)
                    del connection_ids[server_connections[client].id]
                    del server_connections[client]
                except ValueError as error:
                    logger.log('Handler {0}: client {1} disconnected'.format(idx, client.getpeername()))
                    if client in outputs:               
                        outputs.remove(client)                
                    if client in inputs:                                    
                        inputs.remove(client)                
                    del connection_ids[server_connections[client].id]
                    del server_connections[client]                
                    client.close()        
    
            if len(read_messages)>0:
                read_queue.put(read_messages)
    
            for client in writable:            
                try:             
                    if client in server_connections and len(server_connections[client].write_buffer)>0:                    
                        logger.log('Handler {0} write data to client {1}'.format(idx, client.getpeername()))                    
                        write(idx, server_connections[client], logger) 
                        if len(server_connections[client].write_buffer)==0:
                            logger.log('Handler {0}: write buffer for client {1} is empty'.format(idx, client))
    
                            #if buffer is empty go to reading
                            if client in outputs:                            
                                outputs.remove(client)                             
                            #if we wrote whole buffer begin reading  
                            if not client in inputs:                                    
                                inputs.append(client)
                        else:
                            logger.log('Handler {0}: looks like nothing was sent for client {1}'.format(idx, client))
                    #else:
                        #print('Connection write buffer empty')                                   
                except socket.error as error:
                    logger.log("Handler {0}: {1}".format(idx, repr(error)))
                    if client in inputs: 
                        inputs.remove(client)    
                    if client in outputs:  
                        outputs.remove(client)
                    del connection_ids[server_connections[client].id]
                    del server_connections[client]
                except ValueError as error:
                    logger.log('Handler {0}: client {1} disconnected'.format(idx, client.getpeername()))
                    if client in outputs:                
                        outputs.remove(client)
                    if client in inputs:                                    
                        inputs.remove(client)
                    del connection_ids[server_connections[client].id]
                    del server_connections[client]                
                    client.close()
    
            # Handle "exceptional conditions"
            for client in exceptional:
                logger.log('Handling exceptional condition for'.format(client.getpeername()))
                # Stop listening for input on the connection
                inputs.remove(client)            
                outputs.remove(client)
                client.close()
        logger.log('Handler {0}: exit loop'.format(idx)) 
    except Exception as ex:
        logger.log('Handler {0} exception: {1}'.format(idx, ex))      
    