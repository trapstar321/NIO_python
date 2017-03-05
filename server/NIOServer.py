from multiprocessing import Manager,Pool
import socket
from server.handler import run
import datetime
import time

from multiprocessing.reduction import reduce_handle
from server.accept import accept
from common.log_optional import Logger

class Handler(object):
    def __init__(self, idx, manager, pool, client_queue, udp_port, run, forwarder, processor, debug):        
        self.idx=idx
        self.pool=pool
        self.udp_port = udp_port
        self.debug=debug
        
        self.run=run
        self.processor=processor
        self.forwarder=forwarder
        
        self.client_queue=client_queue
        self.read_queue=manager.Queue()
        self.write_queue=manager.Queue()
        self.lock=manager.Lock()
        self.flag=manager.Value('d', 0.0)
        self.stats=manager.Queue()
        
        self.received= manager.Value('d', 0.0)
        self.sent = manager.Value('d', 0.0)
        self.client_cnt = manager.Value('d', 0.0)
    
    def start(self):
        self.pool.apply_async(self.run, (self.idx,self.udp_port, self.flag, self.lock, 
                                         self.client_queue,self.read_queue, self.write_queue, self.debug, self.stats,
                                         self.received, self.sent, self.client_cnt))
        self.pool.apply_async(self.forwarder, (self.udp_port, self.read_queue, self.write_queue, self.processor, self.debug))
        
    def shutdown(self):
        #exit forwarder            
        self.read_queue.put([{}])
        
        #exit if blocked on waiting for first client
        self.client_queue.put({})
        
        #exit if blocked on select
        self.lock.acquire()
        self.flag.value=1.0
        self.lock.release()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b'1', ('127.0.0.1', self.udp_port))
        
class Server(object):
    def __init__(self, port, nHandlers, debug, forwarder, msg_processor):
        self.port = port
        self.nHandlers = nHandlers        
        self.handlers = {}
        self.debug=debug
        self.forwarder=forwarder
        self.processor=msg_processor
        self.start_udp_port = 5001  
        self.client_queue={}
        
        self.manager = Manager()               
        
        self.start_time=0
        self.end_time=0

    def stopwatch_start(self):
        self.start_time=datetime.datetime.now()
        
    def stopwatch_end(self):
        self.end_time=datetime.datetime.now()
        
    def stopwatch_ms(self):
        return (self.end_time-self.start_time).microseconds/1000

    def __initHandlers(self):
        for x in range(self.nHandlers):
            self.client_queue[x]=self.manager.Queue()
            
            self.handlers[x]=Handler(x, self.manager, self.pool, self.client_queue[x], self.start_udp_port, run, self.forwarder, self.processor, self.debug)
            self.handlers[x].start()
            
            self.start_udp_port+=1            
       
    def start(self):
        self.pool = Pool(self.nHandlers*2+1) 
        
        logger = Logger(self.debug)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        server.setblocking(0)
        # TODO change localhost to hostname
        server_address = ('localhost', self.port)
        server.bind(server_address)
        
        logger.log('server: starting server on {0}'.format(server_address))
        
        server.listen(5)
        
        self.__initHandlers()       
        
        h = reduce_handle(self.server.fileno())      
        
        self.start_udp_port+=1
        self.stop_accept_udp_port=self.start_udp_port
        self.pool.apply_async(accept, (h, self.start_udp_port, self.client_queue, self.nHandlers, self.debug)) 
    
    def get_stats(self):
        pings = []
        for x in range(0, self.nHandlers):
            stats = self.handlers[x].stats
            for x in range(0,50):
                ping = stats.get()
                pings.append(ping)
        return pings                
    
    def shutdown(self):
        #exit accept process
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b'1', ('127.0.0.1', self.stop_accept_udp_port))        
        
        for x in range(self.nHandlers):
            handler = self.handlers[x]
            handler.shutdown()
        
        self.pool.close()
        self.pool.join()
        
        self.server.close()
    
    def set_port(self, port):
        self.port=port
        
    def set_n_handlers(self, nHandlers):
        self.nHandlers=nHandlers
       
    def client_count(self, handler):
        h = self.handlers[handler]        
        
        h.lock.acquire()
        cnt = h.client_cnt.value
        h.lock.release()
        
        return cnt
    
    def total_received(self, handler):
        h = self.handlers[handler]        
        
        h.lock.acquire()
        cnt = h.received.value
        h.lock.release()
        
        return cnt
    
    def total_sent(self, handler):
        h = self.handlers[handler]        
        
        h.lock.acquire()
        cnt = h.sent.value
        h.lock.release()
        
        return cnt    
                    
if __name__ == '__main__':
    from server.message_forwarder import forward_messages
    from server.message_processor import process_messages

    try:
        s = Server(10000,1, True, forward_messages, process_messages)
        s.start()        
    except Exception as ex:
        print(ex)   

    #return
    time.sleep(30) 
    s.shutdown()
    #print('Server shutdown complete') 
    #s.start()  
    
    pings = s.get_stats()
        
    print([[x,pings.count(x)] for x in set(pings)])
        
    print('Max ping was {0} ms'.format(max(pings)))
    print('Average ping is: {0}'.format(sum(pings)/float(len(pings))))

