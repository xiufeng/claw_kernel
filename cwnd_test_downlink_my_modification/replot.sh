#!/bin/bash
# 4/14/2015 xxie
# parameter initialization
echo "======plot the tcp probe results"
fileName="snd_cwnd"
plotScript="LinePoints.plt"
gnuplot -e "tmpName='{$fileName}.eps'" $plotScript
inkscape --export-pdf=${fileName}.pdf --export-area-drawing {$fileName}.eps
rm {$fileName}.eps 
