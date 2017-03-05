import struct
import pickle

class ClientMessage(object):   
    INT_SIZE=4
    BOOL_SIZE=1
    LONG_SIZE=4
    BYTE_SIZE=1
    FLOAT_SIZE=4
    DOUBLE_SIZE=8
    SHORT_SIZE=2
    
    def __init__(self, data):
        self.buffer = data
        self.last_pos = 0
        
    def get_int(self):
        data = struct.unpack_from('<I', self.buffer, self.last_pos)[0]
        self.last_pos+=ClientMessage.INT_SIZE
        return data
    
    def get_bool(self):
        data = struct.unpack_from('<?', self.buffer, self.last_pos)[0]
        self.last_pos+=ClientMessage.BOOL_SIZE
        return data
    
    def get_long(self):
        data = struct.unpack_from('<l', self.buffer, self.last_pos)[0]
        self.last_pos+=ClientMessage.LONG_SIZE
        return data
    
    def get_byte(self):
        data = struct.unpack_from('<B', self.buffer, self.last_pos)[0]
        self.last_pos+=ClientMessage.BYTE_SIZE
        return data
    
    def get_float(self):
        data = struct.unpack_from('<f', self.buffer, self.last_pos)[0]
        self.last_pos+=ClientMessage.FLOAT_SIZE
        return data
    
    def get_double(self):
        data = struct.unpack_from('<d', self.buffer, self.last_pos)[0]
        self.last_pos+=ClientMessage.DOUBLE_SIZE
        return data
    
    def get_short(self):
        data = struct.unpack_from('<h', self.buffer, self.last_pos)[0]
        self.last_pos+=ClientMessage.SHORT_SIZE
        return data
    
    def get_string(self):
        str_len = struct.unpack_from('<I', self.buffer, self.last_pos)[0]
        self.last_pos+=ClientMessage.INT_SIZE
        data = struct.unpack_from('<{0}s'.format(str_len), self.buffer, self.last_pos)[0]
        self.last_pos+=str_len
        return data.decode('utf-8')
    
    def get_object(self):
        obj_len = struct.unpack_from('<I', self.buffer, self.last_pos)[0]
        self.last_pos+=ClientMessage.INT_SIZE
        end = self.last_pos+obj_len
        data = self.buffer[self.last_pos:end]
        self.last_pos+=obj_len
        return pickle.loads(data)
        
        
    