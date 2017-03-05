from server.messages.SM_PONG import SM_PONG

def process_messages(messages, client_id):    
    try:
        smessages = []
        for message in messages:
            msg = SM_PONG(message.data)
            smessages.append(msg)
        return smessages
    except Exception as ex:
        print('process_messages exception: {0}'.format(ex))