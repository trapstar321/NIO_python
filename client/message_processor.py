from client.messages.CM_PING import CM_PING

def process_messages(messages):    
    smessages = []
    for message in messages:
        msg = CM_PING(message.data)
        smessages.append(msg)
    return smessages    