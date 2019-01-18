#!/bin/bash 
cd /home/pi/op25/op25/gr-op25_repeater/apps/
./rx.py --args 'rtl' -N 'LNA:47' -S 2400000 -f 478.0000e6 -o 25000 -T /home/pi/pi-scanner/pica_trunk.tsv -V -2 -U 2> stderr.2
