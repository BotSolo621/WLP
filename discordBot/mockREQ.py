import socket
import time

def send_command(command):
    ip = '127.0.0.1'
    port = 4570
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((ip, port))
    server.send(command.encode())
    server.close()

def fetch_response(device, command):
    ip = '127.0.0.1'
    port = 4570
    while True:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((ip, port))
        fetch_cmd = f":FETCHRESPONSE\n{device}\n{command}"
        server.send(fetch_cmd.encode())

        response = server.recv(8192).decode()
        server.close()

        if response.strip() != "No response available yet.":
            return response
        time.sleep(1)  # wait a bit before polling again

# 1. Send the GETSCREENSHOT command
send_command(":GETSCREENSHOT\neppybot")

# 2. Wait and fetch the response
cows = fetch_response("eppybot", "GETSCREENSHOT")
print(cows)
