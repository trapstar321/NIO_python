import queue
from server.messages.CM_PING import CM_PING
from common.log_optional import Logger

def forward_messages(read_queue, write_queue, process_messages, debug):
    logger = Logger(debug)
    while True:
        try:            
            messages = read_queue.get() 
        except queue.Empty:                  
            pass
        else:
            try:  
                processed_messages = []
                for message in messages:
                    processed = process_messages([CM_PING(bytes(message["data"]))], message["id"])
                    for p in processed:
                        processed_messages.append({"id":message["id"], "opcode":type(p).OP_CODE, "data":p.get_data()})
                write_queue.put(processed_messages)         
            except Exception as ex:
                logger.log('forward_messages: exception: {0}'.format(ex))
        
        