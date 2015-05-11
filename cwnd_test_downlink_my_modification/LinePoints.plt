reset
# 3.3in is column width of ACM papers
set terminal postscript landscape size 3.3in,3.3in enhanced mono font "Helvetica,10"
#set output "tmp.eps"
set output tmpName

set size 1.0,0.618 # set figure aspect ratio (w.r.t canvas)
#set border linewidth 0.5
#set border 3
#set tmarg 3
#set bmarg 3
#set lmarg 6
#set rmarg 6


# Dim the border color;
set style line 80 linecolor rgb "#808080" linetype 1
set border linestyle 80 linewidth 0.5

#make the top and right boarder disappear
set border 3 back linestyle 80

# Make tics smaller
set tics scale 0.5
set tics textcolor rgb "black"

# Dim the grid lines
set grid xtics ytics linetype 3 linewidth 0.25 lc rgb "gray"

set key at graph 0.45,0.95
#set key spacing 1
set key samplen 1.5
#set key horizontal 
#set key width -1
#set key box 
#set key width_increment 4
set key left Left reverse

set xlabel 'Time (s)'
set ylabel 'Window Size (Segments)'
#set xrange [0:50]
#set yrange [0:800]


#set xtics nomirror offset 0,0.2 autofreq 0,0.2
#set ytics nomirror offset 0.5,0 autofreq 0,0.2
set tics scale 0.25

set xlabel font "Helvetica,13" offset graph 0,0.00
set ylabel font "Helvetica,13" offset graph 0.00,-0.02
set key font "Helvetica,12"
set key spacing 1.7
set xtics font "Helvetica,13" autofreq 0,20 
set ytics font "Helvetica,13" autofreq 0,100
#set xrange [0:20]

set ytics nomirror
set xtics nomirror

#set key at graph 0.3,0.95
#set key spacing 1.2
#set key samplen 2
set style line 1 lc rgb 'red' lt 1 lw 3
set style line 2 lc rgb 'black' lt 4 lw 2
set style line 3 lc rgb 'blue' lt 12 lw 3
set style line 4 lc rgb 'green' lt 1 lw 2 pt 8 ps 0.40 pi 50
set style line 5 lc rgb 'gold' lt 1 lw 2 pt 6 ps 0.50 pi 50
               
inFileA = "tcpprobe.out"
plot inFileA using 1:7 w l ls 1 title "snd cwnd", \
     inFileA using 1:($8>=2147483647 ? 0 : $8)  w l ls 2 title "snd ssthresh"
#inFileA using 1:4 w l ls 3 title "1000ms Interval",\
#inFileA using 1:5 w lp ls 4 title "5000ms Interval"
