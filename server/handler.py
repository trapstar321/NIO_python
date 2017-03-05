from common.connection import Connection
from common.log_optional import Logger
from common.input_output import read, write, add_messages_to_write_buffer
import queue
import select
import socket
from multiprocessing.reduction import rebuild_handle
import datetime
import time

def close_clients(idx, logger, connections):
    logger.log('Handler {0}: close clients'.format(idx))
    for client in connections:
        client.shutdown(socket.SHUT_RDWR)
        client.close()
    return
    

def run(idx, udp_port, flag, lock, client_queue, read_queue, write_queue, debug, stats, received, sent, client_cnt):    
    logger=Logger(debug)    
        
    logger.log("Start handler {0}".format(idx))
    
    inputs = []
    outputs=[]    
    server_connections = {}   
    connection_ids = {} 
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', udp_port))
    inputs.append(sock)
    
    try:
        while True:    
            try:        
                if len(server_connections)>0:                        
                    h = client_queue.get(False)
                else:
                    h = client_queue.get()
            except queue.Empty:
                pass
            except Exception as ex:
                logger.log(ex) 
            else:  
                if h=={}:
                    logger.log('Handler {0}: exit'.format(idx))
                    close_clients(idx, logger, server_connections)
                    return
                
                fd=rebuild_handle(h)
                client=socket.fromfd(fd,socket.AF_INET,socket.SOCK_STREAM)
                logger.log('Handler {0} got new client {1}'.format(idx, client.getpeername()))                   
                inputs.append(client)
                sc = Connection(client)
                server_connections[client]=sc     
                connection_ids[sc.id]=sc                                       
                
                lock.acquire()
                client_cnt.value+=1
                lock.release()
                           
            try:
                messages = write_queue.get(False)
            except queue.Empty:
                pass
            else:
            #print("To write {0}".format(len(messages)))
                for message in messages:
                    connection = connection_ids[message["id"]]
                    add_messages_to_write_buffer(idx, connection, message, logger)
                    
                    if not connection.connection in outputs:
                        outputs.append(connection.connection)
                    if connection.connection in inputs:
                        inputs.remove(connection.connection)                  
    
            if not inputs and not outputs:                                            
                time.sleep(0.001)
                continue
            
            logger.log('Handler {0}: inputs={1}, outputs={2}'.format(idx, inputs, outputs))
            
            s=datetime.datetime.now()
            readable,writable,exceptional = select.select(inputs, outputs, inputs)
            e=datetime.datetime.now()
            s = (e-s).microseconds/1000
            stats.put(s)
            
            if sock in readable:                                
                sock.recvfrom(8)
                
                lock.acquire()
                exit_ = False
                if flag.value==1.0:
                    logger.log('Handler {0}: exit'.format(idx))
                    close_clients(idx, logger, server_connections)
                    
                    client_cnt.value=0
                    
                    exit_ = True
                lock.release()
                
                if exit_:
                    return
                else:                
                    continue
            
            logger.log('Handler {0}: readable {1}, writable {2}, exceptions {3}'.format(idx, len(readable), len(writable), len(exceptional)))
    
            all_messages=[]
            total_received=0
            for client in readable:                        
                try:
                    logger.log('Handler {0} read data from client {1}'.format(idx, client.getpeername()))
                    val = read(idx, server_connections[client], logger)
                    messages = val['messages']
                    total_received+=val['received']
                    
                    id_ = server_connections[client].id                                
                    logger.log('Handler {0}: processed {1} messages'.format(idx, len(messages)))                    
        
                    for message in messages:
                        message['id']=id_
                    
                    all_messages.extend(messages)                               
                    logger.log('Handler {0}: exit read for client {1}'.format(idx, client.getpeername()))
                except socket.error as error:
                    logger.log("Handler {0} exception: {1}".format(idx, repr(error)))
                    try:
                        if client in inputs: 
                            inputs.remove(client)    
                        if client in outputs:  
                            outputs.remove(client)
                        del connection_ids[server_connections[client].id]
                        del server_connections[client]
                        
                        lock.acquire()
                        client_cnt.value-=1
                        lock.release()
                                                
                    except Exception as ex:
                        logger.log("Handler {0} exception {1}: ".format(idx, repr(ex)))
                except ValueError as error:
                    logger.log('Handler {0}: client {1} disconnected'.format(idx, client.getpeername()))
                    if client in outputs:               
                        outputs.remove(client)                
                    if client in inputs:                                    
                        inputs.remove(client)                
                    del connection_ids[server_connections[client].id]
                    del server_connections[client]                
                    client.close()
                    
                    lock.acquire()
                    client_cnt.value-=1
                    lock.release()
            
            lock.acquire()
            received.value+=total_received      
            lock.release()
            
            if len(all_messages)>0:                
                read_queue.put(all_messages)
            
            total_sent = 0
            for client in writable:
                try:
                    if client in server_connections and len(server_connections[client].write_buffer)>0:                    
                        logger.log('Handler {0} write data to client {1}'.format(idx, client.getpeername()))                    
                        total_sent+=write(idx, server_connections[client], logger) 
                        if len(server_connections[client].write_buffer)==0:
                            logger.log('Handler {0}: write buffer for client {1} is empty'.format(idx, client))    
                            
                            if client in outputs:                            
                                outputs.remove(client)                             
                             
                            if not client in inputs:                                    
                                inputs.append(client)
                        else:
                            logger.log('Handler {0}: looks like nothing was sent for client {1}'.format(idx, client))
                    #else:
                        #print('Connection write buffer empty')                                   
                except socket.error as error:
                    logger.log("Handler {0} exception: {1}".format(idx, repr(error)))
                    try:
                        if client in inputs: 
                            inputs.remove(client)    
                        if client in outputs:  
                            outputs.remove(client)
                        del connection_ids[server_connections[client].id]
                        del server_connections[client]  
                        
                        lock.acquire()
                        client_cnt.value-=1
                        lock.release()                      
                    except Exception as ex:
                        logger.log("Handler {0} exception {1}: ".format(idx, repr(ex)))
                except ValueError as error:
                    logger.log('Handler {0}: client {1} disconnected'.format(idx, client.getpeername()))
                    if client in outputs:                
                        outputs.remove(client)
                    if client in inputs:                                    
                        inputs.remove(client)
                    del connection_ids[server_connections[client].id]
                    del server_connections[client]                
                    client.close()    
                    
                    lock.acquire()
                    client_cnt.value-=1
                    lock.release()
            
            lock.acquire()
            sent.value+=total_sent
            lock.release()
            
            # Handle "exceptional conditions"
            for client in exceptional:
                logger.log('Handling exceptional condition for'.format(client.getpeername()))
                # Stop listening for input on the connection
                inputs.remove(client)            
                outputs.remove(client)
                client.close()
                
                lock.acquire()
                client_cnt.value-=1
                lock.release()
        logger.log('Handler {0}: exit loop'.format(idx)) 
    except Exception as ex:
        print('Handler {0} exception: {1}'.format(idx, ex))      
    