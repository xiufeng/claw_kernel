#!/bin/bash
kill $(pidof iperf3)
iperf3 -s -p 18086
sudo rm /tmp/tcpprobe.out
sudo modprobe -r tcp_probe
sudo modprobe tcp_probe port=18086 full=1
sudo chmod 444 /proc/net/tcpprobe
cat /proc/net/tcpprobe >/tmp/tcpprobe.out &
