"""
https://gist.github.com/sammachin/b67cc4f395265bccd9b2da5972663e6d
http://www.steves-internet-guide.com/into-mqtt-python-client/
"""

import time
from secrets import PASSWORD, SSID
from time import sleep

import network
from as7341_sensor import Sensor
from machine import Pin, unique_id
from neopixel import NeoPixel
from ubinascii import hexlify
from umqtt.simple import MQTTClient

my_id = hexlify(unique_id()).decode()

prefix = f"sdl-demo/{my_id}/"

print(f"prefix: {prefix}")

pixels = NeoPixel(Pin(28), 1)  # 1 pixel on Pin 28

sensor = Sensor()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

# Wait for connect or fail
max_wait = 30
while max_wait > 0:  # type: ignore
    if wlan.status() < 0 or wlan.status() >= 3:  # type: ignore
        break
    max_wait -= 1
    print("waiting for connection...")
    sleep(1)

# Handle connection error
if wlan.status() != 3:  # type: ignore
    raise RuntimeError("network connection failed")
else:
    print("connected")
    status = wlan.ifconfig()
    ip = status[0]  # type: ignore
    print(f"ip: {ip}")


def callback(topic, msg):
    t = topic.decode("utf-8").lstrip(prefix)
    print(t)
    if t[:5] == "GPIO/":
        p = int(t[5:])
        data = int(msg)
        print(data)
        pixels[0] = (data, data, data)
        pixels.write()
        client.publish(prefix + "picow", str(p) + "-" + str(data))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


def heartbeat(first):
    global lastping
    if first:
        client.ping()
        lastping = time.ticks_ms()
    if time.ticks_diff(time.ticks_ms(), lastping) >= 300000:
        client.ping()
        lastping = time.ticks_ms()
    return


client = MQTTClient(
    prefix + "picow/",
    "test.mosquitto.org",
    user=None,
    password=None,
    keepalive=300,
    ssl=False,
    ssl_params={},
)
client.connect()
heartbeat(True)
client.set_callback(callback)
client.on_message = on_message
client.subscribe(prefix + "GPIO/#")
while True:
    msg = client.check_msg()
    heartbeat(False)
