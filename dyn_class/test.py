
class Msg:    
    def __init__(self, data):
        self.data = data
    
class Ping(Msg):
    op_code = 22
    
    def __init__(self, data):
        super(Ping, self).__init__(data)
        
    def get_data(self):
        return self.data

class Pong(Msg):
    op_code = 23
    
    def __init__(self, data):
        super(Pong, self).__init__(data)
        
    def get_data(self):
        return self.data

if __name__ == '__main__':
    classes = [Ping, Pong]
    
    ping = classes[0]("Ping")
    pong = classes[1]("Pong")
    
    op_code = 23
    
    for x in classes:
        if x.op_code==op_code:
            inst = x("Data")
            print(type(inst))
    
    
    