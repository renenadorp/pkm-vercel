|What | Command| Comment |
|--|--|--|
| Count files |  `ls \| wc -l `|
| List Devices on network | `arp -a`| 
| Dump network traffic | `tcpdump`|
| Check if device is online | `nmap <ip>` | Requires nmap.|
| Ports in use |`sudo lsof -i -n -P \| grep TCP`| Requires root privileges|
| Show all processes | `​ps -ef​` ||