from multiprocessing import Manager, Pool
import socket
from NIO_python.client.handler import run
#from multiprocessing.reduction import reduce_handle
import datetime
import time
#from NIO_python.client.messages.CM_PING import CM_PING
import multiprocessing
multiprocessing.allow_connection_pickling()

class Handler(object):
    def __init__(self, client, manager, pool, udp_port, run, forwarder, processor, debug):
        self.idx=1
        self.client = client
        self.pool=pool
        self.udp_port = udp_port

        self.debug=debug        
        
        self.run=run
        self.processor=processor
        self.forwarder=forwarder
        self.read_queue=manager.Queue()
        self.write_queue=manager.Queue()
        self.lock=manager.Lock()
        self.flag=manager.Value('d', 0.0)
        self.pings=manager.Queue()        
    
    def start(self):
        client = self.client
        self.pool.apply_async(self.run, (1, client, self.udp_port, self.lock, self.flag, self.debug, self.read_queue, self.write_queue, self.pings))
        if self.forwarder is not None:
            self.pool.apply_async(self.forwarder, (self.udp_port, self.read_queue, self.write_queue, self.processor, self.debug, self.pings))
        
    def shutdown(self):
        #exit forwarder            
        self.read_queue.put([{}])
        
        #exit if blocked on select
        self.lock.acquire()
        self.flag.value=1.0
        self.lock.release()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b'1', ('127.0.0.1', self.udp_port))

class Client(object):
    udp_port=10000

    def __init__(self, server_address, udp_port, debug, forwarder, msg_processor):
        if udp_port is None:
            Client.udp_port+=1
            self.udp_port = Client.udp_port
        else:
            self.udp_port = udp_port

        self.server_address = server_address
        self.client = None        
        self.debug=debug
        self.forwarder=forwarder
        self.msg_processor=msg_processor
        self.handler=None
        
        self.manager = Manager()         
        
        self.start_time=0
        self.end_time=0

    def stopwatch_start(self):
        self.start_time=datetime.datetime.now()
        
    def stopwatch_end(self):
        self.end_time=datetime.datetime.now()
        
    def stopwatch_ms(self):
        return (self.end_time-self.start_time).microseconds/1000

    def __initHandler(self):  
        #h = reduce_handle(self.client.fileno())
        self.handler = Handler(self.client, self.manager, self.pool, self.udp_port, run, self.forwarder, self.msg_processor, self.debug)
        self.handler.start()
        
    def start(self):
        self.pool=Pool()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        s = datetime.datetime.now()        
        client.connect(self.server_address)
        e=datetime.datetime.now()
        #print('Connect took {0}'.format((e-s).microseconds/1000))
        self.client = client
        client.setblocking(0)
        
        #print('Connected to server on {0}'.format(self.server_address))
        
        self.__initHandler()
        #client.close()
    
    
    def shutdown(self):
        self.handler.shutdown()
        
        self.pool.close()
        self.pool.join()
        
    def get_stats(self):
        pings=[]
        for x in range(0,20):
            ping = self.handler.pings.get()
            pings.append(ping)
        return pings
           
if __name__ == '__main__':    
    from client.message_forwarder import forward_messages
    from client.message_processor import process_messages
    
    clients = []
    
    #for x in range(0,1):
    c = Client(("localhost", 10000), True, forward_messages, process_messages)
    clients.append(c)
    c.start()

    msg = CM_PING("a"*32)
    c.handler.write_queue.put([{"opcode":type(msg).OP_CODE, "data":msg.get_data()}])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b'1', ('127.0.0.1', c.udp_port))

    while True:
        time.sleep(1)
        
        # time.sleep(2)
        # c.shutdown()
        #
        # time.sleep(2)
        # c.start()
        #
        # msg = CM_PING("a"*32)
        # c.handler.write_queue.put([{"opcode":type(msg).OP_CODE, "data":msg.get_data()}])
        #
        # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # sock.sendto(b'1', ('127.0.0.1', c.udp_port))
        
    # time.sleep(20)
    # c.shutdown()
    #
    # time.sleep(10)
    #
    # for c in clients:
    #     pings = []
    #     pings.extend(c.get_stats())
    #
    #     print([[x,pings.count(x)] for x in set(pings)])
    #
    #     print('Max ping was {0} ms'.format(max(pings)))
    #     print('Average ping was {0} is: {1}'.format(c, sum(pings)/float(len(pings))))
    #
    # #4 processes = 2.17 ms
    # #1 processes = 2.34 ms
    # #2 processes = 2.62 ms
    # #3 processes = 1.74 ms
    # #5 processes = 2.03 ms
    # #8 processes = 2.15 ms
        
    
    
    
        
    
    


