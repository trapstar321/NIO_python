import unittest
from client.NIOClient import Client
from messages.client.CM_PING import CM_PING
import time
import datetime

start=None
end=None

def _process_messages(messages):
    global start
    global end
    global pings
    
    if start:
        end = datetime.datetime.now()    
        ping = (end-start).microseconds/1000              
    start = datetime.datetime.now()
    
    smessages = []
    for message in messages:     
        smessages.append(CM_PING("a"*32))    
    return smessages

class PingTest(unittest.TestCase):
    def test_ping(self):
        global _process_messages
        c = Client(("localhost", 10000), False, _process_messages, CM_PING("a"*32))
        c.start()   
        time.sleep(0.4)      
        print(end)  
        