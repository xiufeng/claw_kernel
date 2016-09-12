from __future__ import division
import socket
import sys
import pickle

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('0.0.0.0', 23456)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

fallback_thresh=0.7

while True:
    print >>sys.stderr, '\nCLAW server waiting to receive message'
    data, address = sock.recvfrom(4096)

    message = pickle.loads(data)
    snd_cwnd_increase = message[0]
    cqic_win = message[1]
    claw_win = message[3]
    rsrq_used = message[4]
    rsrq_used_self = message[5]
    new_win = int(message[6])

    # compute the use ratio
    if(rsrq_used>0):
	    use_ratio = rsrq_used_self/rsrq_used 
    else:
	    use_ratio = -1 

    # if other use takes too many, we should go to aggressive fallback
    if use_ratio<fallback_thresh:
	fallback_mode=1
	print >>sys.stderr, 'fallback on, self use ratio %f' % (use_ratio) 
    else:
	fallback_mode=0
	print >>sys.stderr, 'no fallback, self use ratio %f' % (use_ratio) 

    fo2 = open("/proc/sys/net/ipv4/tcp_fallback", "wb")
    fo2.write(str(fallback_mode));
    fo2.close()

    # get current time
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])

    print >>sys.stderr, 'received %s bytes from %s at time %f' % (len(data), address, uptime_seconds)
    print >>sys.stderr, 'remaining %d, self use %d, self use ratio %f, cqic win %d claw win %d' % (snd_cwnd_increase, rsrq_used_self, use_ratio, cqic_win, claw_win)

    # write tcp_rate only in CLAW state
    # Open a file
    fo = open("/proc/sys/net/ipv4/tcp_rate", "wb")
    # sysctl can only write string
    fo.write(str(claw_win));
    #fo.write(str(new_win));
    print >>sys.stderr, 'write, claw win %f' % (claw_win) 
    # Close opend file
    fo.close()


    fo2 = open("/proc/sys/net/ipv4/tcp_add", "wb")
    fo2.write(str(snd_cwnd_increase));
    fo2.close()

    # write message to text file
    fo_log = open("/home/ubuntu/feedback.log", "a+")
    fo_log.write(('%f 1\n')%(uptime_seconds));
    fo_log.close()

    #ack_message = "ACK of snd_cwnd increase"
    
    #if data:
    #    sent = sock.sendto(ack_message, address)
    #    print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)
