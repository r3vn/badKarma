# badKarma - advanced network reconnaissance toolkit #
[![Python 3](https://img.shields.io/badge/python-3-green.svg)](https://www.python.org/) 
[![License](https://img.shields.io/badge/license-GPLv3-red.svg)](https://github.com/r3vn/badKarma/blob/master/license.md)
[![Twitter](https://img.shields.io/badge/twitter-@r3vnn-blue.svg)](https://twitter.com/r3vnn)

<img align="left" src="https://github.com/r3vn/badKarma/blob/master/assets/images/icon.png?raw=true">

badKarma is a python3 GTK+ toolkit that aim to assist penetration testers during all the network infrastructure penetration testing activity phases.
It allow testers to save time by having point-and-click access to their toolkits, launch them against single or multiple targets and interacte with them through semplified GUIs or Terminals.


Every task's output is logged under a session file in order to help during reporting phase or in a possible incident response scenario. 
It is also available a proxychains switch that let everything go through proxies, and last but not least, every command can be adjusted before the execution by disabling the "auto-execute" checkbox.

badKarma is licensed under GNU GPL version 3.

## Session file ##
The Session file is just a sqlite database, it contains all the information gained during the activity, real-time updated it can be exported or/and imported from badKarma's GUI.
By default the database is located inside the "/tmp" directory, this means that you have to save it in a different location before rebooting your computer. 

Inside the database there are four tables: hosts, ports, activity_log and notes.

## Targets ##
It is possible to add targets and scan them with nmap and/or masscan from the GUI, some defaults scan profiles are already available as well. 
It is possible to import XML scanners result from the main menu.

There is also a shodan-api's script (smap.py) that let the tester importing target's data directly from shodan. It is located inside the scripts directory and it require a shodan api key inside conf/shodan.conf in order to work.

By default all the scan output are stored inside the "/tmp" directory , then the output is imported in the session file and deleted.

## Extensions ##
badKarma is modular, the extensions are full-interactive and they allow the penetration tester to tune tasks options, since output is logged under the session file, their output can be exported as a raw txt from the "Logs" tab. 

Extensions can be found under the "extension" directory,current available extensions are: 
 - __Shell:__ this is the main module of the toolkit since it allow the tester to execute preconfigured shell tasks. Shell commands are located under the "conf" directory.
 - __Bruter:__ as the name says, bruter is the brute-force extension. It allow the tester to send a target directly to Hydra and configure the parameters through a GUI.
 Default hydra parameters can be modified from conf/bruter.conf.
 - __Screenshot:__ this extension allow the tester to take screenshots of possibile http,rdp,rtsp,vnc and x11 servers, screenshots will be stored in the session file as base64 and can be shown from badKarma.
 - __Browser:__ just an "open in browser" for http menu item, take it as an example to build your own extensions.

## Screenshots ##
<p align="center">
<img width="710" src="https://user-images.githubusercontent.com/635790/45002099-7161df80-afd3-11e8-8131-a4dfd8090562.gif">
</p>

<p align="center">
<img width="350" src="https://user-images.githubusercontent.com/635790/44464652-a6f1ea80-a61b-11e8-9180-126c97e8aacc.png">
<img width="350" src="https://user-images.githubusercontent.com/635790/44464653-a6f1ea80-a61b-11e8-8bb2-dbf0d58f3720.png">
<img width="350" src="https://user-images.githubusercontent.com/635790/44618508-74442e00-a877-11e8-8a6c-1b241aac9de1.png">
<img width="350" src="https://user-images.githubusercontent.com/635790/44618566-aefa9600-a878-11e8-98c1-55d619277903.png">
<img width="350" src="https://user-images.githubusercontent.com/635790/44464655-a78a8100-a61b-11e8-980f-53ec8eb3da87.png">
<img width="350" src="https://user-images.githubusercontent.com/635790/44464656-a78a8100-a61b-11e8-9975-3d6e5573a690.png"></p>

## Setup ##
install Kali linux dependecies:
```bash
# apt install python3-pip python3-gi phantomjs gir1.2-gtk-vnc-2.0 gir1.2-gtksource-3.0 gir1.2-vte-2.91 ffmpeg 
```
clone the repository:
```bash
$ git clone https://github.com/r3vn/badKarma.git
```
install python dependecies:
```bash
# cd badKarma
# pip3 install -r requirements.txt
```

## Run ##
```bash
$ chmod +x badkarma.py
$ ./badkarma.py
```

## Donate ##

<img align="right" src="https://user-images.githubusercontent.com/635790/45373809-a207d180-b5f0-11e8-9b12-20462d720b45.png">
If you appreciated my work, you can buy me a beer. I accept Ƀitcoins to 1Dvvb3TGHRQwfLoUT8rVTPmHqgVjAJRcsm.
