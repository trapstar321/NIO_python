import server.messages.CM_PING
import client.messages.CM_PING

msg = client.messages.CM_PING.CM_PING("a"*32)
print(msg.get_data())

b = bytearray(msg.get_data())
print(bytes(b))
print(server.messages.CM_PING.CM_PING(msg.get_data()).data)

d = {'a':1, 'b':2}
print(len(d))

from multiprocessing import Queue

q = Queue()

q.put(1)
q.put(2)
q.put(3)
q.put(4)

q.get()
#q.close()
q.get()

from multiprocessing import Pipe
a,b=Pipe()

b.poll(0.1)

a.send(1)
print(b.recv())


#kill handler, stop reading
#stop forwarder, process queue, write to write queue and exit

inputs=[]
outputs=[]

if not inputs and not outputs:
    print('OK')