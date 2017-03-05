import struct
import pickle

from messages.server.server_message import ServerMessage
from messages.server.client_message import ClientMessage
from messages.server.SM_TEST import SM_TEST
from messages.server.CM_TEST import CM_TEST

from dyn_class.test import Pong
name = 'Jadrejčić'

b = bytearray()
encoded=name.encode('utf-8')
str_len_in_b = len(encoded)

#integer
b.extend(struct.pack('<I', str_len_in_b))
#float
b.extend(struct.pack('<f', 3.5))
#double
b.extend(struct.pack('<d', 5.5))
#long
b.extend(struct.pack('<l', 1234567890))
#short
b.extend(struct.pack('<h',25))
#byte
b.extend(struct.pack('<B', 255))
#bool
b.extend(struct.pack('<?', False))
#string
b.extend(encoded)
#bytes
b.extend([1,2,3,4,5])


str_len = struct.unpack_from('<I', b, 0)[0]
fl = struct.unpack_from('<f', b, 4)[0]
dbl = struct.unpack_from('<d', b, 8)[0]
long = struct.unpack_from('<l', b, 16)[0]
short = struct.unpack_from('<h', b, 20)[0]
byte = struct.unpack_from('<B', b, 22)[0]
bool = struct.unpack_from('<?', b, 23)[0]
name = struct.unpack_from('<{0}s'.format(str_len), b,24)[0]
#print(str_len)
#print(fl)
#print(dbl)
#print(long)
#print(short)
#print(byte)
#print(bool)
#print(name.decode('utf-8'))
#print(b[24+str_len:24+str_len+5])
#print(by)

#y = bytearray()
#y.extend([1,2,3,4,5])
#print(by[0:-2])

#smessage = ServerMessage()
#smessage.put_int(33)
#smessage.put_bool(True)
#smessage.put_long(1234567890)
#smessage.put_byte(22)
#smessage.put_bytes([1,2,3,4,5])
#smessage.put_float(3.5)
#smessage.put_double(310.55)
#smessage.put_string('Jadrejčić')
#smessage.put_short(-1)
#smessage.put_object(Pong("You pinged?"))

#cmessage = ClientMessage(smessage.get_data())
#print(cmessage.get_int())
#print(cmessage.get_bool())
#print(cmessage.get_long())
#print(cmessage.get_byte())
#print(cmessage.get_float())
#print(cmessage.get_double())
#print(cmessage.get_string())
#print(cmessage.get_short())
#obj = cmessage.get_object()
#print(obj.get_data())

smessage = SM_TEST(33, True, 1234567890, 22, 3.5, 310.55, 'Jadrejčić', -1, 'You pinged?')
cmessage = CM_TEST(smessage.get_data())

print(cmessage.int_)
print(cmessage.bool_)
print(cmessage.long_)
print(cmessage.byte_)
print(cmessage.float_)
print(cmessage.double_)
print(cmessage.string_)
print(cmessage.short_)
print(cmessage.object_)

tb = bytearray()
tb.extend(b'!\x00\x00\x00')
tb.extend(b'!\x00\x00\x00')

print(tb)
print(len(tb))

a=1
b=1
c=1

print(tb[0:4])
