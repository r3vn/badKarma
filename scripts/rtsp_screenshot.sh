#!/bin/bash
# rtsp screenshot

ffmpeg -loglevel fatal -i rtsp://$1:$2/ -vframes 1 -r 1 /tmp/badkarma-screenshot-$1-$2.jpg
base64 /tmp/badkarma-screenshot-$1-$2.jpg
rm /tmp/badkarma-screenshot-$1-$2.jpg
