import socket
import sys
import pickle

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('0.0.0.0', 23456)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# current state, 0 is CLAW, 1 is Cubic
cur_state=1 # use CLAW by default
last_state=1 # use CLAW by default
keep_no_resource=0 #if we always have no res, go to Cubic
keep_full_resource=0 #if we always have full res, go to CLAW

state_change_thresh=3

while True:
    print >>sys.stderr, '\nCLAW server waiting to receive message'
    data, address = sock.recvfrom(4096)

    message = pickle.loads(data)
    snd_cwnd_increase = message[0]
    cqic_win = message[1]
    claw_win = message[3]


    #state criteria
    if snd_cwnd_increase<20: # no resource
	keep_no_resource=keep_no_resource+1
	keep_full_resource=0
    elif snd_cwnd_increase>200:
	keep_full_resource=keep_full_resource+1
	keep_no_resource=0
    else:
	keep_full_resource=0
	keep_no_resource=0

    #state transfter
    if keep_no_resource>state_change_thresh and cur_state==1:
	cur_state=0
	# clear all variables
	keep_full_resource=0
	keep_no_resource=0
    elif keep_full_resource>state_change_thresh and cur_state==0:
	cur_state=1
	# clear all variables
	keep_full_resource=0
	keep_no_resource=0
	
    #state change from CLAW to Cubic
    if cur_state==0 and last_state==1:
	# turn off tcp_lte
	fo = open("/proc/sys/net/ipv4/tcp_lte", "wb")
	fo.write(str(0));
	fo.close()
        print >>sys.stderr, 'CLAW off' 

	# turn on fallbacok
	fo2 = open("/proc/sys/net/ipv4/tcp_fallback", "wb")
	fo2.write(str(1));
	fo2.close()
        print >>sys.stderr, 'fallback on' 

    #state change from Cubic to CLAW
    if cur_state==1 and last_state==0:
	# turn on tcp_lte
	fo = open("/proc/sys/net/ipv4/tcp_lte", "wb")
	fo.write(str(1));
	fo.close()
        print >>sys.stderr, 'CLAW on' 

    
    print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
    print >>sys.stderr, 'remaining %d, cqic win %d claw win %d, keep no %d, keep full %d cur state %d, last state %d' % (snd_cwnd_increase, cqic_win, claw_win, keep_no_resource, keep_full_resource, cur_state, last_state)

    # write tcp_rate only in CLAW state
    if cur_state==1:
	    # Open a file
	    fo = open("/proc/sys/net/ipv4/tcp_rate", "wb")
	    # sysctl can only write string
	    fo.write(str(claw_win));
	    print('write done')
	    # Close opend file
	    fo.close()


    fo2 = open("/proc/sys/net/ipv4/tcp_add", "wb")
    fo2.write(str(snd_cwnd_increase));
    fo2.close()

    #update the last state
    last_state=cur_state

    #ack_message = "ACK of snd_cwnd increase"
    
    #if data:
    #    sent = sock.sendto(ack_message, address)
    #    print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)
