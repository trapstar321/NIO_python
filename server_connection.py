from uuid import uuid1

class ServerConnection(object):
    def __init__(self, connection):
        self.id = uuid1()
        self.connection=connection
        self.buffer=bytearray()
        self.position=0 
        
        
        self.write_buffer = bytearray()              
        
    