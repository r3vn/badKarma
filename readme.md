# badKarma - advanced network reconnaissance toolkit #

badKarma is a python3 GTK+ graphical toolkit made in order to simplifies and automate network infrastructure penetration testing.
badKarma aim to help the tester in all the penetration testing phases (information gathering, vulnerability assessment,exploitation,post-exploitation and reporting). It allow the tester to save time by having point-and-click access to their toolkit and interacte with them through GUIs or Terminals, also every task is logged under a sqlite database in order to help the tester in the reporting phase or in a incident response scenario. 
It is available a proxychains switch that let everything go through proxies, and last but not least, every commands can be customized before execution by disabling the "auto-execute" switch.
badKarma is licensed under GNU GPL version 3.

### Database ###
The database by default is located inside the "/tmp" directory, this means obivously that you have to save it in a different location before rebooting your computer. 
It contains all the information gained during the activity, real-time updated, it is used like a session file, and it can be exported or/and imported.

### Targets ###
It is possible to add target and scan them with nmap or import an nmap XML report, also some defaults scan profiles are already available as well. 
By defaults all the nmap output are stored inside the "/tmp" directory , then the output is imported in the sqlite database and deleted.

### Extensions ###
badKarma is modular, the extensions are fully interactive and customizable, also every extension output is logged under the database and can be exported as a raw txt from the "Logs" tab. 
Extensions can be found under the "extension" directory,current available extensions are: 
 - __Shell:__ this is the main module of the toolkit since it allow the tester to execute both automated and manual tasks. Shell command are located under the "conf" directory and can be fully customized.
 - __Bruter:__ as the name says, bruter allow the tester to send a target directly to Hydra, the interface is graphical, additional parameters are available and hydra output is logged in the sqlite database.
 - __Screenshot:__ this extension allow the tester to take a screenshot of possibile web servers, the screenshot will be stored in the log database as base64 and can be normally shown from badKarma.
 - __Browser:__ just an "open in browser" for webservers menu item, take it as an example to build your own extensions.

## Screenshots ##



## Setup ##
install Kali linux dependecies:
```bash
# apt install python3-pip python3-gi phantomjs gir1.2-gtk-vnc-2.0 ffmpeg `
```
install python dependecies:
```bash
# pip3 install -r requirements.txt
```

Also dirsearch is required by the shell extension:
 - https://github.com/maurosoria/dirsearch

## Run ##
```bash
$ chmod +x badkarma.py
$ ./badkarma.py
```