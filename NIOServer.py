from multiprocessing import Manager,Pool
import socket
import select
import queue
from dispatcher import run
from server_connection import ServerConnection
from messages.server.SM_TEST import SM_TEST
from messages.server.SM_PONG import SM_PONG
import datetime

from messages.server.CM_PING import CM_PING

from dyn_class.test import Pong

from multiprocessing.reduction import reduce_handle

class Server(object):
    def __init__(self, port, nDispatchers):
        self.port = port
        self.nDispatchers = nDispatchers        
        self.client_queue = {}
        self.server = None
        
        self.manager = Manager()
        self.pool = Pool()
        
        self.lastDispatcher=-1
        self.start_time=0
        self.end_time=0

    def stopwatch_start(self):
        self.start_time=datetime.datetime.now()
        
    def stopwatch_end(self):
        self.end_time=datetime.datetime.now()
        
    def stopwatch_ms(self):
        return (self.end_time-self.start_time).microseconds/1000

    def __initDispatchers(self):
        
        for x in range(self.nDispatchers):
            client_queue=self.manager.Queue()                 
            self.pool.apply_async(run, (x,client_queue, False))
            self.client_queue[x]=client_queue 
       
    def __getDispatcher(self):                
        if self.lastDispatcher==self.nDispatchers-1:            
            self.lastDispatcher=0;
        else:        
            self.lastDispatcher+=1;
        return self.lastDispatcher;     
        
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
            #print('Waiting for next client')
            readable,writable,exceptional = select.select(inputs, [],[])
    
            for s in readable:
                if s is server:
                    connection, client_address = s.accept()
                    connection.setblocking(0) 
                    print('New connection from {0}'.format(client_address))                                      
                    
                    dispatcher = self.__getDispatcher()
                    print('Last dispatcher={0}'.format(dispatcher))
                    
                    print('Add connection {0} to dispatcher {1}'.format(client_address, dispatcher))
                    
                    h = reduce_handle(connection.fileno())                 
                    
                    self.client_queue[dispatcher].put(h)
                    #connection.close()               
                else:
                    print('Select returned {0}'.format(s))
        
if __name__ == '__main__':
    s = Server(10000,1)
    s.start()


