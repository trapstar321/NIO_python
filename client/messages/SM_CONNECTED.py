from NIO_python.client.messages.server_message import ServerMessage


class SM_CONNECTED(ServerMessage):
    OP_CODE = 1

    def __init__(self, data):
        ServerMessage.__init__(self, data)

        self.idx = self.get_string()


