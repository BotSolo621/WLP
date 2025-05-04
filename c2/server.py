import socket

ip = '127.0.0.1'# this is for local hosting, for the actual server host, use 0.0.0.0
port = 4570

# Dict to store info per machine
pcInfos = {}
# List of all machine IDs that have ever connected
machine_list = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((ip, port))
server_socket.listen(5)

print(f"[+] Server listening on {ip}:{port}")

while True:
    client_socket, address = server_socket.accept()
    print(f"[+] Connection from {address}")

    msg = client_socket.recv(4096).decode()
    print(f"[<] Received:\n{msg}")

    if msg.startswith(":PCINFO"):
        content = msg[len(":PCINFO"):].strip()
        lines = content.split('\n')
        machine_id = lines[0]
        info = '\n'.join(lines[1:])
        pcInfos[machine_id] = info

        if machine_id not in machine_list:
            machine_list.append(machine_id)
            print(f"[+] New machine added: {machine_id}")
        else:
            print(f"[=] Existing machine updated: {machine_id}")

    elif msg.startswith(":GETINFO"):
        response = ""
        for machine_id, info in pcInfos.items():
            response += f"[{machine_id}]\n{info}\n\n"
        client_socket.send(response.encode())

    elif msg.startswith(":LISTCOWS"):
        response = "\n".join(machine_list)
        client_socket.send(response.encode())

    client_socket.close()
