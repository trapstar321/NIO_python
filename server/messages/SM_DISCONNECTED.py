from NIO_python.server.messages.server_message import ServerMessage


class SM_DISCONNECTED(ServerMessage):
    OP_CODE = 2

    def __init__(self, idx):
        ServerMessage.__init__(self)

        self.put_string(idx)
