from multiprocessing import Queue
import socket
import select
from dispatch import Dispatcher


class Server(object):
    def __init__(self, port, nDispatchers):
        self.port = port
        self.nDispatchers = nDispatchers
        self.dispatchers = []
        self.clientQueue = {}
        self.server = None
        
        self.lastDispatcher=0

    def __initDispatchers(self):
        for x in range(self.nDispatchers):
            q=Queue()      
            d=Dispatcher(q, x)
            self.clientQueue[x]=q
            self.dispatchers.append(d)
            d.start()
       
    def __getDispatcher(self):        
        if self.lastDispatcher==len(self.dispatchers)-1:
            self.lastDispatcher=0;
            return self.dispatchers[self.lastDispatcher];
        else:
            self.lastDispatcher+=1;
            return self.dispatchers[self.lastDispatcher];        
        
    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        server.setblocking(0)
        # TODO change localhost to hostname
        server_address = ('localhost', self.port)
        server.bind(server_address)
        
        print('Starting server on {0}'.format(server_address))
        
        server.listen(5)
        
        self.__initDispatchers()
        
        inputs = [server]        
        
        while inputs:
            print('Waiting for next client')
            readable,writable,exceptional = select.select(inputs, [],[])
    
            for s in readable:
                if s is server:
                    connection, client_address = s.accept()
                    connection.setblocking(0) 
                    print('New connection from {0}', client_address)                                      
                    
                    dispatcher = self.__getDispatcher()
                    print('Last dispatcher={0}'.format(self.lastDispatcher))
                    
                    print('Add connection {0} to dispatcher {1}'.format(client_address, dispatcher.getID()))
                    
                    self.clientQueue[dispatcher.getID()].put(connection)
                    #connection.close()               
                else:
                    print('Select returned {0}'.format(s))


if __name__ == '__main__':
    s = Server(10000,4)
    s.start()


