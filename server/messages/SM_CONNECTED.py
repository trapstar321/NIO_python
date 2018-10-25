from NIO_python.server.messages.server_message import ServerMessage


class SM_CONNECTED(ServerMessage):
    OP_CODE = 1

    def __init__(self, idx):
        ServerMessage.__init__(self)

        self.put_object(idx)
