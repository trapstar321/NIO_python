import socket
import sys

messages = [ 'This is the message. ',
             'It will be sent ',
             'in parts.',
             ]
server_address = ('localhost', 10000)

# Create a TCP/IP socket
socks = [ socket.socket(socket.AF_INET, socket.SOCK_STREAM),
          socket.socket(socket.AF_INET, socket.SOCK_STREAM),
          ]

# Connect the socket to the port where the server is listening
print('connecting to %s'.format(server_address))
for s in socks:
    s.connect(server_address)
    
for message in messages:

    # Send messages on both sockets
    for s in socks:
        print('{0} sending {1}'.format(s.getsockname(), message))
        s.send(message.encode('UTF-8'))

    # Read responses on both sockets
    for s in socks:
        data = s.recv(1024)
        print('{0} received {1}'.format(s.getsockname(), data))
        if not data:
            print('closing socket {0}'.format(s.getsockname()))
            s.close()    