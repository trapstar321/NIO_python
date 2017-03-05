import struct 

buffer = bytearray()

buffer.extend(struct.pack('<I', 55))
buffer.extend(struct.pack('<I', 66))
buffer.extend(struct.pack('<I', 77))

print(len(buffer)) 

print(len(buffer[5:-1]))

print("a"*32)

import time

time1 = time.time()
time.sleep(0.001)
time2 = time.time()

print(time2-time1)

import multiprocessing

print(multiprocessing.cpu_count())