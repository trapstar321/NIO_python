from messages.client.client_message import ClientMessage

class CM_TEST(ClientMessage):
    OP_CODE=24
    
    def __init__(self, int_, bool_, long_, byte_, float_, double_, string_, short_, object_):
        ClientMessage.__init__(self)
        
        self.put_int(int_)
        self.put_bool(bool_)
        self.put_long(long_)
        self.put_byte(byte_)
        self.put_float(float_)
        self.put_double(double_)
        self.put_string(string_)
        self.put_short(short_)
        self.put_object(object_)