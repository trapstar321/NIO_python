from common.connection import Connection
from common.log_optional import Logger
from common.input_output import read, write, add_messages_to_write_buffer
import time
import select
import socket
import datetime
#from multiprocessing.reduction import rebuild_handle
import queue

n=0

import multiprocessing
multiprocessing.allow_connection_pickling()

#flag values:
# 1 = shutdown request
# 4 = exited
# 2 = started
# 3 = disconnected

def notify_disconnected(lock, flag):
    lock.acquire()
    flag.value = 3
    lock.release()


def notify_started(lock, flag):
    lock.acquire()
    flag.value = 2
    lock.release()


def notify_exited(lock, flag):
    lock.acquire()
    flag.value = 4
    lock.release()


def run(idx, client, udp_port, lock, flag, debug, read_queue, write_queue, pings):
    notify_started(lock, flag)
    
    logger=Logger(debug)    
       
    logger.log("Start handler {0}".format(idx))
    
    inputs = []
    outputs=[]
    
    #fd=rebuild_handle(handle)
    #client=socket.fromfd(fd,socket.AF_INET,socket.SOCK_STREAM)
    connection = Connection(client)
   
    inputs.append(client)
   
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', udp_port))
    inputs.append(sock)
    
    try:
        while True:                    
            try:
                messages = write_queue.get(False)
            except queue.Empty:
                pass
            else:                            
                for message in messages:                    
                    add_messages_to_write_buffer(idx, connection, message, logger)
                
                if len(messages)>0:    
                    if not connection.connection in outputs:
                        outputs.append(connection.connection)
                    if connection.connection in inputs:
                        inputs.remove(connection.connection)        
            
            if not inputs and not outputs:                         
                time.sleep(0.001)
                continue            
            
            logger.log('Handler {0}: inputs={1}, outputs={2}'.format(idx, len(inputs), len(outputs)))
            
            readable,writable,exceptional = select.select(inputs, outputs, inputs)
            
            logger.log('Handler {0}: readable {1}, writable {2}, exceptions {3}'.format(idx, len(readable), len(writable), len(exceptional)))
            
            if sock in readable:                                
                sock.recvfrom(8)
                
                lock.acquire()
                exit_ = False
                if flag.value==1.0:
                    logger.log('Handler {0}: exit'.format(idx))
                    client.shutdown(socket.SHUT_RDWR)
                    client.close()                    
                    exit_ = True
                lock.release()
                
                if exit_:
                    notify_exited(lock, flag)
                    return
                else:                
                    continue
            
            all_messages=[]
            
            for client in readable:                        
                try:
                    logger.log('Handler {0} read data from client {1}'.format(idx, client.getpeername()))
                    
                    val = read(idx, connection, logger)
                    messages = val['messages']
                    #received = val['received']
                    
                    all_messages.extend(messages)
                    
                    logger.log('Handler {0}: processed {1} messages'.format(idx, len(messages)))
                               
                    logger.log('Handler {0}: exit read for client {1}'.format(idx, client.getpeername()))
                except socket.error as error:
                    logger.log(repr(error))
                    if client in outputs:               
                        outputs.remove(client)                
                    if client in inputs:                                    
                        inputs.remove(client)
                    notify_disconnected(lock, flag)
                    return
                except ValueError as error:
                    logger.log('Handler {0}: client {1} disconnected'.format(idx, client.getpeername()))
                    if client in outputs:               
                        outputs.remove(client)                
                    if client in inputs:                                    
                        inputs.remove(client)                
                    client.close()
                    notify_disconnected(lock, flag)
                    return
                
            if len(all_messages)>0:                
                read_queue.put(all_messages)
         
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
                    notify_disconnected(lock, flag)
                    return
                except ValueError as error:
                    logger.log('Handler {0}: client {1} disconnected'.format(idx, client.getpeername()))
                    if client in outputs:                
                        outputs.remove(client)
                    if client in inputs:                                    
                        inputs.remove(client)
                    client.close()
                    notify_disconnected(lock, flag)
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
    notify_exited(lock, flag)
    