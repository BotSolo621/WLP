import platform
import socket
from requests import get

ip = '127.0.0.1'
port = 4570

cow = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cow.connect((ip, port))
PCinfo = ":GETINFO 1"
cow.send(PCinfo.encode())
cow.close()

#Exmple
#:PCINFO
#DESKTOP-K5B43CV
#System: Windows
#Release: 10
#Version: 10.0.19045
#Machine: AMD64
#Processor: Intel64 Family 6 Model 165 Stepping 5, GenuineIntel
#IP: xxx.xx.xxx.xxx