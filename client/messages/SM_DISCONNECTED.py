from NIO_python.client.messages.server_message import ServerMessage


class SM_DISCONNECTED(ServerMessage):
    OP_CODE = 2

    def __init__(self, data):
        ServerMessage.__init__(self, data)

        self.idx = self.get_object()
