import socket

def connect(command):
    ip = '127.0.0.1'
    port = 4570
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((ip, port))
    server.send(command.encode())

    try:
        response = server.recv(8192).decode()
    except:
        response = "No response"
    server.close()
    return response

connect(":GETINFO")