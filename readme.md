# badKarma - advanced network reconnaissance toolkit #

<img align="left" src="https://github.com/r3vn/badKarma/blob/master/assets/images/icon.png?raw=true">

badKarma is a python3 GTK+ network infrastructure penetration testing toolkit.

badKarma aim to help the tester in all the penetration testing phases (information gathering, vulnerability assessment,exploitation,post-exploitation and reporting). It allow the tester to save time by having point-and-click access to their toolkit and interacte with them through GUIs or Terminals, also every task is logged under a sqlite database in order to help during the reporting phase or in a incident response scenario. 

It is also available a proxychains switch that let everything go through proxies, and last but not least, every commands can be adjusted before the execution by disabling the "auto-execute" checkbox.

badKarma is licensed under GNU GPL version 3.

### Database ###
The database by default is located inside the "/tmp" directory, this means that you have to save it in a different location before rebooting your computer. 

It contains all the information gained during the activity, real-time updated, it is used like a session file, and it can be exported or/and imported.

### Targets ###
It is possible to add target and scan them with nmap or import an nmap XML report, also some defaults scan profiles are already available as well. 

By defaults all the nmap output are stored inside the "/tmp" directory , then the output is imported in the sqlite database and deleted.

### Extensions ###
badKarma is modular, the extensions are full-interactive and they allow the tester to tune tasks options, also every extension output is logged under the database and can be exported as a raw txt from the "Logs" tab. 

Extensions can be found under the "extension" directory,current available extensions are: 
 - __Shell:__ this is the main module of the toolkit since it allow the tester to execute preconfigured shell tasks. Shell commands are located under the "conf" directory.
 - __Bruter:__ as the name says, bruter is the brute-force extension. It allow the tester to send a target directly to Hydra and configure the parameters through a GUI.
 - __Screenshot:__ this extension allow the tester to take a screenshot of possibile web servers, the screenshot will be stored in the log database as base64 and can be normally shown from badKarma.
 - __Browser:__ just an "open in browser" for webservers menu item, take it as an example to build your own extensions.

## Screenshots ##
<p align="center">
<img width="710" src="https://user-images.githubusercontent.com/635790/44618869-604ffa80-a87e-11e8-8387-0fa8f12a0aa7.gif">
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
# apt install python3-pip python3-gi phantomjs gir1.2-gtk-vnc-2.0 ffmpeg `
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