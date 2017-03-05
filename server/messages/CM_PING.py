from server.messages.client_message import ClientMessage

class CM_PING(ClientMessage):
    OP_CODE=26
    
    def __init__(self, data):
        ClientMessage.__init__(self, data)

        self.data = self.get_string()        
        
 