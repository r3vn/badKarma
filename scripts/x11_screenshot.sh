#!/bin/bash
# X11screenshot
# -------------
# This script came from SPARTA and will take a screenshot over a remote X11 server, 
# save it to an output folder and print the base64 of the file
# 
# Original author:
# SECFORCE - Antonio Quina

if [ $# -eq 0 ]
	then
		echo "Usage: $0 <IP> <DISPLAY>"
		echo "eg: $0 10.10.10.10 0 /outputfolder"
		exit
	else
		IP="$1"
fi

if [ "$2" == "" ]
	then
		DSP="0"
	else
		DSP="$2"
fi

if [ "$3" == "" ]
	then
		OUTFOLDER="/tmp"
	else
		OUTFOLDER="$3"
fi

xwd -root -screen -silent -display $IP:$DSP > $OUTFOLDER/x11screenshot-$IP.xwd

if [ -f $OUTFOLDER/x11screenshot-$IP.xwd ]; then
	convert $OUTFOLDER/x11screenshot-$IP.xwd $OUTFOLDER/x11screenshot-$IP.jpg
	base64 $OUTFOLDER/x11screenshot-$IP.jpg
fi