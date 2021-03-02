import network
from iothub import *

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('', '')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

connect_wifi()


## Parse the connection string into constituent parts
connection_string = ""

print("connecting to IoT Hub")

def c2d_cb(msg):
    print(msg)
    
client = IothubClient(connection_string)
client.connect();
client.set_c2d_cb(c2d_cb)
client.send_telemetry("msg")