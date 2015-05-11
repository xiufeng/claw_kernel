#!/bin/bash
# 4/14/2015 xxie
# parameter initialization
HOSTNAME=54.68.125.63
PEMPATH=./xxf1.pem
DUR=100
SWITCHTIME=50
LEFTTIME=$((DUR-SWITCHTIME))
TRACELOCLOC=./tcpprobe.out
PASSKEY=64x65x89f
chmod 400 $PEMPATH
#clean the remote kernel log
ssh -i $PEMPATH ubuntu@$HOSTNAME -f 'sudo sh -c "echo '' > kern.log"'
#set the value of the prb we want to send (0 to 63)
#echo $PASSKEY | sudo -S sysctl -w net.ipv4.tcp_prb=40
# turn off ECN on both sides
echo "======configure ECN on both sides"
echo $PASSKEY | sudo -S sysctl -w net.ipv4.tcp_ecn=0 
ssh -i $PEMPATH ubuntu@$HOSTNAME -f 'sudo sysctl -w net.ipv4.tcp_ecn=0'
# turn off your modification on both sides in the beginning
ssh -i $PEMPATH ubuntu@$HOSTNAME -f 'sudo sysctl -w net.ipv4.tcp_lte=0'
echo $PASSKEY | sudo -S sysctl -w net.ipv4.tcp_lte=0 
#assign the sender and receiver (local (TCP receiver) and remote EC2 machine (TCP sender))
ssh -i $PEMPATH ubuntu@$HOSTNAME -f 'sudo sysctl -w net.ipv4.tcp_tx=1'
echo $PASSKEY | sudo -S sysctl -w net.ipv4.tcp_tx=0 
echo "======start iperf server at the server $HOSTNAME"
ssh -i $PEMPATH ubuntu@$HOSTNAME 'bash -s' < ./activate_tcpprobe.sh&
#wait the server to be ready
sleep 5
echo "======start iperf client and tcpdump at local machine"
iperf3 -c $HOSTNAME -p 18086 -R -t $DUR &
# dump the received packets for throughput evaluation
sudo tcpdump -i usb0 -w /home/xiufeng/dump_received_packets &
# turn on your modification half way
sleep $SWITCHTIME
ssh -i $PEMPATH ubuntu@$HOSTNAME -f 'sudo sysctl -w net.ipv4.tcp_lte=1'
echo $PASSKEY | sudo -S sysctl -w net.ipv4.tcp_lte=1 
sleep $LEFTTIME
# download and plot the results
echo "======download the tcp probe results from the server to local machine"
ssh -i $PEMPATH ubuntu@$HOSTNAME -f 'sudo kill $(pidof cat)'
scp -i $PEMPATH ubuntu@$HOSTNAME:/tmp/tcpprobe.out $TRACELOCLOC
echo "======plot the tcp probe results"
fileName="snd_cwnd"
plotScript="LinePoints.plt"
gnuplot -e "tmpName='{$fileName}.eps'" $plotScript
inkscape --export-pdf=${fileName}.pdf --export-area-drawing {$fileName}.eps
rm {$fileName}.eps 
# download the dmesg to view the prb at the sender
#scp -i $PEMPATH ubuntu@$HOSTNAME:/var/log/kern.log .
#gvim kern.log
