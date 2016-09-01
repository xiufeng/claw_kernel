import socket
import sys
import pickle

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('0.0.0.0', 23456)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# the last tbs value
last_avg_tbs=0
win_scaling_factor=0

while True:
    print >>sys.stderr, '\nclaw server waiting to receive message'
    data, address = sock.recvfrom(4096)

    message = pickle.loads(data)
    snd_cwnd_increase = message[0]
    avg_tbs = message[2]
    
    print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)

    # compute the scaling factor
    # if the tbs is too small, we should not scale
    if avg_tbs<200:
	    win_scaling_factor = 0

    # if last value is initialized and large enough, scale
    # scaling factor has value 1-100 since kernel does not accept float number
    if last_avg_tbs>=200 and avg_tbs>=200:
	    win_scaling_factor = int((float(avg_tbs)/float(last_avg_tbs))*100)

    print >>sys.stderr, 'win increase %d, avg tbs %d, scaling factor %d percent' % (snd_cwnd_increase, avg_tbs, win_scaling_factor)

    # Open a file
    fo = open("/proc/sys/net/ipv4/tcp_add", "wb")
    # sysctl can only write string
    fo.write(str(snd_cwnd_increase));
    print('write done')
    # Close opend file
    fo.close()

    # write the scaling factor only when it has been updated
    if win_scaling_factor>0:
	    fo = open("/proc/sys/net/ipv4/tcp_scale", "wb")
	    # sysctl can only write string
	    fo.write(str(win_scaling_factor));
	    print('write done')
	    # Close opend file
	    fo.close()

    # update the last tbs value
    last_avg_tbs=avg_tbs

    #ack_message = "ACK of snd_cwnd increase"
    
    #if data:
    #    sent = sock.sendto(ack_message, address)
    #    print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)
