import struct
import pickle

class ServerMessage(object):
    def __init__(self):
        self.buffer = bytearray();
        
    def put_int(self, data):
        self.buffer.extend(struct.pack('<I', data))
        
    def put_bool(self, data):
        self.buffer.extend(struct.pack('<?', data))
        
    def put_byte(self, data):
        self.buffer.extend(struct.pack('<B', data))
        
    def put_short(self, data):
        self.buffer.extend(struct.pack('<h', data))
        
    def put_long(self, data):
        self.buffer.extend(struct.pack('<l', data))
        
    def put_float(self, data):
        self.buffer.extend(struct.pack('<f', data))
        
    def put_double(self, data):
        self.buffer.extend(struct.pack('<d', data))
        
    def put_string(self, data):
        encoded = data.encode('utf-8')
        self.buffer.extend(struct.pack('<I', len(encoded)))
        self.buffer.extend(encoded)
        
    def put_object(self, data):
        serialized = pickle.dumps(data)
        self.buffer.extend(struct.pack('<I', len(serialized)))
        self.buffer.extend(serialized)
        
    def get_data(self):
        return bytes(self.buffer)   
     