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

# current state, 0 is CLAW, 1 is Cubic
cur_state=1 # use CLAW by default
last_state=1 # use CLAW by default
keep_no_resource=0 #if we always have no res, go to Cubic
keep_full_resource=0 #if we always have full res, go to CLAW

state_change_thresh=2
no_resource_thresh=50
full_resource_thresh=200

last_claw_win=0

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


    #state criteria
    if snd_cwnd_increase<no_resource_thresh: # no resource
        #do not count resources if we are on the idle channel
	if snd_cwnd_increase==-1:
		keep_no_resource=0
	else:
		keep_no_resource=keep_no_resource+1
	keep_full_resource=0
    elif snd_cwnd_increase>full_resource_thresh:
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

	# turn on fallbacok
	# if other use takes too many, we should go to aggressive fallback
	if use_ratio<0.8:
		#fallback_mode=100
		#print >>sys.stderr, 'fallback to slow start, self use ratio %f' % (use_ratio) 
		fallback_mode=0
		cur_state=1
		print >>sys.stderr, 'no fallback, self use ratio %f' % (use_ratio) 
	else:
		fallback_mode=0
		cur_state=1
		print >>sys.stderr, 'no fallback, self use ratio %f' % (use_ratio) 


	fo2 = open("/proc/sys/net/ipv4/tcp_fallback", "wb")
	fo2.write(str(fallback_mode));
	fo2.close()
        #print >>sys.stderr, 'fallback on' 

	# turn off tcp_lte
	if cur_state==0:
		fo = open("/proc/sys/net/ipv4/tcp_lte", "wb")
		fo.write(str(0));
		fo.close()
		print >>sys.stderr, 'CLAW off' 

    #state change from Cubic to CLAW
    if cur_state==1 and last_state==0:
	# turn on tcp_lte
	fo = open("/proc/sys/net/ipv4/tcp_lte", "wb")
	fo.write(str(1));
	fo.close()
        print >>sys.stderr, 'CLAW on' 

    
    print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
    print >>sys.stderr, 'remaining %d, cqic win %d claw win %d, keep no %d, keep full %d cur state %d, last state %d, self use %d, self use ratio %f' % (snd_cwnd_increase, cqic_win, claw_win, keep_no_resource, keep_full_resource, cur_state, last_state, rsrq_used_self, use_ratio)

    # write tcp_rate only in CLAW state
    if cur_state==1:
	    # lock the window
	    #if(claw_win<0.4*last_claw_win):
	#	claw_win=last_claw_win
		
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

    #update the last state
    last_state=cur_state
    last_claw_win=claw_win

    #ack_message = "ACK of snd_cwnd increase"
    
    #if data:
    #    sent = sock.sendto(ack_message, address)
    #    print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)
