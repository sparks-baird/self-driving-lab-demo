"""
https://gist.github.com/sammachin/b67cc4f395265bccd9b2da5972663e6d
http://www.steves-internet-guide.com/into-mqtt-python-client/
"""

import json
from secrets import PASSWORD, SSID
from time import sleep, ticks_diff, ticks_ms

import network
from as7341_sensor import Sensor
from machine import Pin, unique_id
from neopixel import NeoPixel
from ubinascii import hexlify
from umqtt.simple import MQTTClient

my_id = hexlify(unique_id()).decode()

prefix = f"sdl-demo/picow/{my_id}/"

print(f"prefix: {prefix}")

pixels = NeoPixel(Pin(28), 1)  # one NeoPixel on Pin 28 (GP28)

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


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(prefix + "GPIO/#")


def callback(topic, msg):
    t = topic.decode("utf-8").lstrip(prefix)
    print(t)
    if t[:5] == "GPIO/":
        p = int(t[5:])
        print(msg)
        data = json.loads(msg)
        r, g, b = [data[key] for key in ["R", "G", "B"]]
        pixels[0] = (r, g, b)
        pixels.write()

        payload = json.dumps(
            dict(pin=p, r=r, g=g, b=b, sensor_data=sensor.all_channels)
        )

        print(payload)

        client.publish(prefix + "as7341/", payload)


def heartbeat(first):
    global lastping
    if first:
        client.ping()
        lastping = ticks_ms()
    if ticks_diff(ticks_ms(), lastping) >= 300000:
        client.ping()
        lastping = ticks_ms()
    return


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


client = MQTTClient(
    prefix,
    "test.mosquitto.org",
    user=None,
    password=None,
    keepalive=0,
    ssl=False,
    ssl_params={},
)
client.connect()
client.set_callback(callback)
client.on_connect = on_connect
client.on_message = on_message
client.subscribe(prefix + "GPIO/#")

heartbeat(True)

while True:
    client.check_msg()
    heartbeat(False)

# heartbeat(True)

# while True:
#     heartbeat(False)
