from messages.client.server_message import ServerMessage
from messages.client.client_message import ClientMessage
from messages.client.SM_TEST import SM_TEST
from messages.client.CM_TEST import CM_TEST

cmessage = CM_TEST(33, True, 1234567890, 22, 3.5, 310.55, 'Jadrejčić', -1, 'You pinged?')
smessage = SM_TEST(cmessage.get_data())

print(smessage.int_)
print(smessage.bool_)
print(smessage.long_)
print(smessage.byte_)
print(smessage.float_)
print(smessage.double_)
print(smessage.string_)
print(smessage.short_)
print(smessage.object_)