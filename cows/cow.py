import time
import keyboard
import requests

device_name = "boos"
while keyboard.is_pressed("`") == False:
    try:
        requests.get(f"http://localhost:8080/ping?device={device_name}")
        print("Ping sent.")
    except:
        print("Ping attempt failed.")
    time.sleep(5)

