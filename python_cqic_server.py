import socket
import sys
import pickle

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('0.0.0.0', 23456)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

while True:
    print >>sys.stderr, '\nCQIC server waiting to receive message'
    data, address = sock.recvfrom(4096)

    message = pickle.loads(data)
    snd_cwnd_increase = message[0]
    cqic_win = message[1]
    claw_win = message[3]
    
    print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
    print >>sys.stderr, 'cqic win %d claw wind %d' % (cqic_win, claw_win)

    # Open a file
    fo = open("/proc/sys/net/ipv4/tcp_rate", "wb")
    # sysctl can only write string
    fo.write(str(cqic_win));
    print('write done')
    # Close opend file
    fo.close()

    #ack_message = "ACK of snd_cwnd increase"
    
    #if data:
    #    sent = sock.sendto(ack_message, address)
    #    print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)
