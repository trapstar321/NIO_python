import struct

INT_SIZE = 4 
BYTE_SIZE= 1

def read(idx, server_connection, logger):
    connection=server_connection.connection                  
    data = connection.recv(2048)
    
    read_messages = []
    
    logger.log("Handler {0}: buffer={1}".format(idx, server_connection.buffer))        
    logger.log("Handler {0}: read {1} bytes".format(idx, len(data)))
    logger.log("Handler {0}: read {1}".format(idx, data))
    
    if not data:
        raise ValueError('Client disconnected')
    
    server_connection.buffer.extend(data)

    length=0
    opcode=0
    
    while server_connection.position<len(server_connection.buffer):
        left = len(server_connection.buffer)-server_connection.position
        logger.log("Handler {0}: left={1}".format(idx, left))
        
        #ima header
        if left>=5:
            length = struct.unpack_from('<I', server_connection.buffer, server_connection.position)[0]
            server_connection.position+=INT_SIZE
            opcode = struct.unpack_from('<B', server_connection.buffer, server_connection.position)[0]
            server_connection.position+=BYTE_SIZE
            
            #ima i podataka            
            if left-(INT_SIZE+BYTE_SIZE)>=length:
                start = INT_SIZE+BYTE_SIZE
                messageData = server_connection.buffer[start:length+start];
                
                server_connection.position+=length
                
                logger.log("Handler {0}: read message, opcode={1}, length={2} data={3}".format(idx, opcode, length, messageData))                    
                logger.log("Handler {0}: at position: {1}".format(idx, server_connection.position))
                read_messages.append({"opcode":opcode, "data":messageData, "client":server_connection})                
                
                if len(server_connection.buffer)>length+start:
                    logger.log("Handler {0}: got parts of new message.".format(idx))                    
                    logger.log("Handler {0}: current buffer={1}".format(idx, server_connection.buffer))                   
                                        
                    tmp = server_connection.buffer[length+start:len(server_connection.buffer)]
                    server_connection.buffer=bytearray()
                    server_connection.buffer.extend(tmp)
                    server_connection.position=0
                    logger.log("Handler {0}: current buffer length is {1}".format(idx, len(server_connection.buffer)))
                else:
                    logger.log("Handler {0}: reset buffer".format(idx))
                    server_connection.position=0
                    server_connection.buffer=bytearray()
                    break;                   
                                    
            #nema podataka pa utrpaj ostatak u buffer    
            else:
                logger.log("Handler {0}: opcode={1}, length={2}. Whole message not yet received".format(idx, opcode, length))                    
                logger.log("Handler {0}: at position: {1}".format(idx, server_connection.position))                    
                logger.log("Handler {0}: message not complete".format(idx))
                
                server_connection.position=0
                break                
        #nema headera, utrpaj ostatak u buffer
        else:               
            logger.log("Handler {0}: message not complete, put received back to buffer".format(idx))
            break                
    
    logger.log("Handler {0}: buffer: {1}".format(idx, server_connection.buffer))
    
    ret_val = {}
    ret_val['received']= len(data)
    ret_val['messages']=read_messages   
    return ret_val
    
def write(idx, server_connection, logger):    
    if len(server_connection.write_buffer)!=0:
        logger.log('Handler {0}: send {1} to client {2}'.format(idx, server_connection.write_buffer, server_connection.connection))
        sent = server_connection.connection.send(server_connection.write_buffer)                
        
        logger.log('Handler {0}: sent {1} bytes to client {2}'.format(idx, sent, server_connection.connection))
        
        #if not all buffer was sent then compact array
        if sent!=len(server_connection.write_buffer):            
            #compact buffer
            server_connection.write_buffer=server_connection.write_buffer[sent: len(server_connection.write_buffer)]
            logger.log('Handler {0}: not whole buffer was sent for client {1}'.format(idx, server_connection.connection))
        elif sent==0:
            raise ValueError('Client disconnected')
        else:
            logger.log('Handler {0}: whole buffer was sent for client {1}'.format(idx, server_connection.connection))
            server_connection.write_buffer=bytearray()
        return sent            
    #else:
        #logger.log('Handler {0}: write buffer for client {1} is empty'.format(idx, server_connection.connection))
    return 0
        
def add_messages_to_write_buffer(idx, server_connection, message, logger):
    logger.log("Handler {0}: send message {1}".format(idx, message))

    buffer = bytearray()                
    buffer.extend(struct.pack('<I', len(message["data"])))                
    buffer.extend(struct.pack('<B', message["opcode"]))
    buffer.extend(message["data"])

    #logger.log("Handler {0}: add {1} to write buffer for client {1}".format(idx, buffer, client))
    
    write_buffer = server_connection.write_buffer
    write_buffer.extend(buffer)
    #logger.log("Handler {0}: write buffer for {1} is {2}".format(idx, client, write_buffer))
                           
   