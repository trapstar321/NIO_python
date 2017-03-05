import struct
from server_connection import ServerConnection
from log_optional import Logger
import queue
from multiprocessing import Queue
import time
import datetime
import select
import socket
from messages.server.CM_TEST import CM_TEST
from messages.server.SM_PONG import SM_PONG
from messages.server.client_message import ClientMessage
from multiprocessing.reduction import rebuild_handle 

def run(idx, client_queue, debug):    
    logger=Logger(debug)    
        
    logger.log("Start dispatcher {0}".format(idx))
    
    inputs = []
    outputs=[]    
    server_connections = {}    
    
    while True:
        #add new client to input list            
        start_ = datetime.datetime.now()
        try:
            h = client_queue.get_nowait()
            fd=rebuild_handle(h)
            client=socket.fromfd(fd,socket.AF_INET,socket.SOCK_STREAM)
        except queue.Empty:
            pass
        except Exception as ex:
            logger.log(ex) 
        else:  
            logger.log('Dispatcher {0} got new client {1}'.format(idx, client.getpeername()))                   
            inputs.append(client)
            sc = ServerConnection(client)
            server_connections[client]=sc                                            
                        
        if not inputs:                                   
            continue        

        logger.log('Dispatcher {0}: inputs={1}, outputs={2}'.format(idx, len(inputs), len(outputs)))    
            
        readable,writable,exceptional = select.select(inputs, outputs, inputs)
        
        logger.log('Dispatcher {0}: readable {1}, writable {2}, exceptions {3}'.format(idx, len(readable), len(writable), len(exceptional)))
        
        for client in readable:                        
            try:
                logger.log('Dispatcher {0} read data from client {1}'.format(idx, client.getpeername()))
                messages = read(idx, server_connections[client], logger)
                logger.log('Dispatcher{0}: processed {1} messages'.format(idx, len(messages)))                
                messages = process_messages(messages)                
                add_messages_to_write_buffer(idx, server_connections[client], messages, logger)
                dummy_messages(server_connections[client])    
                if not client in outputs:
                    logger.log('Dispatcher {0}: add client {1} to write select list'.format(idx, client))
                    outputs.append(client)     
                           
                logger.log('Dispatcher {0}: exit read for client {1}'.format(idx, client.getpeername()))
            except socket.error as error:
                logger.log(repr(error))
                inputs.remove(client)                    
                # TODO handle message queue
            except ValueError as error:
                logger.log('Client {0} disconnected'.format(client.getpeername()))
                if client in outputs:               
                    outputs.remove(client)                
                if client in inputs:                                    
                    inputs.remove(client)                
                client.close()
                del server_connections[client]                                                  
            else:            
                if client not in outputs:
                    outputs.append(client)
        
        for client in writable:            
            try:             
                if client in server_connections:                    
                    write(idx, server_connections[client], logger) 
                    if len(server_connections[client].write_buffer)==0:
                        logger.log('Dispatcher {0}: write buffer for client {1} is empty'.format(idx, client))
                        outputs.remove(client)                                       
            except socket.error as error:
                logger.log(repr(error))
                inputs.remove(client)                    
                # TODO handle message queue
            except ValueError as error:
                logger.log('Client {0} disconnected'.format(client.getpeername()))
                if client in outputs:                
                    outputs.remove(client)
                if client in inputs:                                    
                    inputs.remove(client)
                client.close()                                    
                del server_connections[client]

        # Handle "exceptional conditions"
        for client in exceptional:
            logger.log('Handling exceptional condition for'.format(client.getpeername()))
            # Stop listening for input on the connection
            inputs.remove(client)            
            outputs.remove(client)
            client.close()
            
        end_ = datetime.datetime.now()
        logger.log('Dispatcher {0}: loop took {1} ms'.format(idx, (end_-start_).microseconds/1000))
           
def read(idx, server_connection, logger):
    connection=server_connection.connection                  
    data = connection.recv(2048)
    
    read_messages = []
    
    logger.log("Dispatcher {0}: buffer={1}".format(idx, server_connection.buffer))        
    logger.log("Dispatcher {0}: read {1} bytes".format(idx, len(data)))
    logger.log("Dispatcher {0}: read {1}".format(idx, data))
    
    if not data:
        raise ValueError('Client disconnected')
    
    server_connection.buffer.extend(data)

    length=0
    opcode=0
    message_data=0
    
    while server_connection.position<len(server_connection.buffer):
        left = len(server_connection.buffer)-server_connection.position
        logger.log("Dispatcher {0}: left={1}".format(idx, left))
        
        #ima header
        if left>=5:
            length = struct.unpack_from('<I', server_connection.buffer, server_connection.position)[0]
            server_connection.position+=ClientMessage.INT_SIZE
            opcode = struct.unpack_from('<B', server_connection.buffer, server_connection.position)[0]
            server_connection.position+=ClientMessage.BYTE_SIZE
            
            #ima i podataka
            if left-ClientMessage.INT_SIZE+ClientMessage.BYTE_SIZE>=length:
                start = ClientMessage.INT_SIZE+ClientMessage.BYTE_SIZE
                messageData = server_connection.buffer[start:length+start];
                
                server_connection.position+=length
                
                logger.log("Dispatcher {0}: read message, opcode={1}, length={2} data={3}".format(idx, opcode, length, messageData))                    
                logger.log("Dispatcher {0}: at position: {1}".format(idx, server_connection.position))
                read_messages.append({"opcode":opcode, "data":messageData, "client":server_connection.id})                
                
                if len(server_connection.buffer)>length+start:
                    logger.log("Dispatcher {0}: probably got parts of new message. Put it in buffer".format(idx))                    
                    logger.log("Dispatcher {0}: current buffer={1}".format(idx, server_connection.buffer))                        
                    tmp = server_connection.buffer[length+start:len(server_connection.buffer)]
                    server_connection.buffer=bytearray()
                    server_connection.buffer.extend(tmp)
                    server_connection.position=0
                    logger.log("Dispatcher {0}: current buffer length is {1}".format(idx, len(server_connection.buffer)))                    
                else:
                    logger.log("Dispatcher {0}: reset buffer".format(idx))
                    server_connection.position=0
                    server_connection.buffer=bytearray()
                    break;
                
                # TODO: implement raising of message receive event
                #notifyClientReceivedListeners(opcode, messageData, connection.getClientID());                    
            #nema podataka pa utrpaj ostatak u buffer    
            else:
                logger.log("Dispatcher {0}: opcode={1}, length={2}. Whole message not yet received".format(idx, opcode, length))                    
                logger.log("Dispatcher {0}: at position: {1}".format(idx, server_connection.position))                    
                logger.log("Dispatcher {0}: message not complete, put received back to buffer".format(idx))
                
                server_connection.position=0
                break                
        #nema headera, utrpaj ostatak u buffer
        else:               
            logger.log("Dispatcher {0}: message not complete, put received back to buffer".format(idx))
            break                
    
    logger.log("Dispatcher {0}: buffer: {1}".format(idx, server_connection.buffer))    
    return read_messages
    
def write(idx, server_connection, logger):    
    if len(server_connection.write_buffer)!=0:
        sent = server_connection.connection.send(server_connection.write_buffer)                
        
        logger.log('Dispatcher {0}: sent {1} bytes to client {2}'.format(idx, sent, server_connection.connection))
        
        #if not all buffer was sent then compact array
        if sent!=len(server_connection.write_buffer):            
            #compact buffer
            server_connection.write_buffer=server_connection.write_buffer[sent: len(server_connection.write_buffer)]
            logger.log('Dispatcher {0}: not whole buffer was sent for client {1}'.format(idx, server_connection.connection))
        elif sent==0:
            raise ValueError('Client disconnected')
        else:
            logger.log('Dispatcher {0}: whole buffer was sent for client {1}'.format(idx, server_connection.connection))
            server_connection.write_buffer=bytearray()            
    else:
        logger.log('Dispatcher {0}: write buffer for client {1} is empty'.format(idx, server_connection.connection))
        
def add_messages_to_write_buffer(idx, server_connection, messages, logger):
    for message in messages:
        logger.log("Dispatcher {0}: send message {1}".format(idx,message))
        client=server_connection.connection                  
        
        buffer = bytearray()                
        buffer.extend(struct.pack('<I', len(message.get_data())))                
        buffer.extend(struct.pack('<B', type(message).OP_CODE))
        buffer.extend(message.get_data())
        logger.log("Dispatcher {0}: add {1} to write buffer for client {1}".format(idx, buffer, client))
        
        write_buffer = server_connection.write_buffer
        write_buffer.extend(buffer)
        logger.log("Dispatcher {0}: write buffer for {1} is {2}".format(idx, client, write_buffer))
                           
def process_messages(messages):
    #return SM_TEST(33, True, 1234567890, 22, 3.5, 310.55, 'Jadrejcic', -1, Pong('You pinged?'))   
    smessages = []
    for message in messages:     
        smessages.append(SM_PONG("a"*32))    
    return smessages
                            
def dummy_messages(server_connection):
    buffer = bytearray()                
    buffer.extend(struct.pack('<I', 41))                
    buffer.extend(struct.pack('<B', 26))
    buffer.extend(struct.pack('<I', 32))
    buffer.extend(("a"*32).encode('utf-8'))    
    
    write_buffer = server_connection.write_buffer
    write_buffer.extend(buffer)    