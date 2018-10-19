from server.messages.SM_PONG import SM_PONG
from common.log_optional import Logger

def process_messages(messages, client_id):    
    try:
        smessages = []
        for message in messages:
            print("Processor received message: {0}".format(message))
            #msg = SM_PONG(message.data)
            #smessages.append(msg)
        return smessages
    except Exception as ex:
        print('process_messages exception: {0}'.format(ex))