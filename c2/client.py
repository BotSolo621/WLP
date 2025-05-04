import socket

ip = '127.0.0.1'
port = 4570

cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cs.connect((ip, port))

msg = 'nigger'
cs.send(msg.encode())

cs.close()