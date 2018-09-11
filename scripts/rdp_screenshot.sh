#!/bin/bash
#
# RDP-screenshotter.sh - version 0.2 BETA(28-08-2016)
# Copyright (c) 2016 Zer0-T
# License: GPLv3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

if [ -z $1 ]; then
    echo "Usage: $0 target.ip"
    exit 1
fi

# Configurable options
output="output"
timeout=60
timeoutStep=2
host=$1
port=$2
blue="\e[34m[*]\e[0m"
red="\e[31m[*]\e[0m"
green="\e[32m[*]\e[0m"
temp="/tmp/${host}.png"

export XAUTHORITY="$XDG_CACHE_HOME/Xauthority"

function screenshot {
    screenshot=$1
    window=$2
    import -window ${window} "${screenshot}"
}

function isAlive {
    pid=$1
    kill -0 $pid 2>/dev/null
    if [ $? -eq 1 ]; then
        exit 1
    fi
}

function isTimedOut {
    t=$1
    if [ $t -ge $timeout ]; then
        kill $!
        exit 1
    fi
}

export DISPLAY=:1

# Launch rdesktop in the background
rdesktop -u "" -a 16 $host &
pid=$!

# Get window id
window=
timer=0
    while true; do
    # Check to see if we timed out
    isTimedOut $(printf "%.0f" $timer)

   # Check to see if the process is still alive
    isAlive $pid
    window=$(xdotool search --name ${host})
    if [ ! "${window}" = "" ]; then
        break
    fi
    timer=$(echo "$timer + 0.1" | bc)
    sleep 0.1
done

# If the screen is all black delay timeoutStep seconds
timer=0
while true; do

    # Make sure the process didn't die
    isAlive $pid

    isTimedOut $timer

    # Screenshot the window and if the only one color is returned (black), give it chance to finish loading
    screenshot "${temp}" "${window}"
    colors=$(convert "${temp}" -colors 5 -unique-colors txt:- | grep -v ImageMagick)
    if [ $(echo "${colors}" | wc -l) -eq 1 ]; then
        sleep $timeoutStep
    else
        # Many colors should mean we've got a console loaded
        break
    fi
    timer=$((timer + timeoutStep))
done


if [ ! -d "${output}" ]; then
    mkdir "${output}"
fi

afterScreenshot="${output}/${host}.png"
screenshot "${afterScreenshot}" "${window}"

# run ocr on saved image(s)
base64 ${temp}

rm ${temp}

# Close the rdesktop window
kill $pid
