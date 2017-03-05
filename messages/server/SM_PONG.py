from messages.server.server_message import ServerMessage

class SM_PONG(ServerMessage):
    OP_CODE=25
    
    def __init__(self, data):
        ServerMessage.__init__(self)        

        self.put_string(data)
