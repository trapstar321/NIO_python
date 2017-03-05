from server.messages.server_message import ServerMessage
from server.messages.client_message import ClientMessage
from server.messages.SM_TEST import SM_TEST
from server.messages.CM_TEST import CM_TEST

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