from client.messages.server_message import ServerMessage

class SM_TEST(ServerMessage):
    OP_CODE=23
    
    def __init__(self, data):
        ServerMessage.__init__(self, data)
        
        self.int_= self.get_int()
        self.bool_ = self.get_bool()
        self.long_ = self.get_long()
        self.byte_ = self.get_byte()
        self.float_ = self.get_float()
        self.double_ = self.get_double()
        self.string_ = self.get_string()
        self.short_ = self.get_short()
        self.object_ = self.get_object()
        
 