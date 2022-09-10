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

try:
    onboard_led = Pin("LED", Pin.OUT)  # only works for Pico W
except Exception as e:
    print(e)
    onboard_led = Pin(25, Pin.OUT)

CHANNEL_NAMES = [
    "ch410",
    "ch440",
    "ch470",
    "ch510",
    "ch550",
    "ch583",
    "ch620",
    "ch670",
]

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

        # payload = json.dumps(
        #     dict(pin=p, r=r, g=g, b=b, sensor_data=sensor.all_channels)
        # )
        sensor_data = sensor.all_channels
        sensor_data_dict = {}
        for ch, datum in zip(CHANNEL_NAMES, sensor_data):
            sensor_data_dict[ch] = datum

        payload = json.dumps(sensor_data_dict)

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


def sign_of_life(first):
    global last_blink
    if first:
        onboard_led.on()
        last_blink = ticks_ms()
    time_since = ticks_diff(ticks_ms(), last_blink)
    if onboard_led.value() == 0 and time_since >= 5000:
        onboard_led.toggle()
        last_blink = ticks_ms()
    elif onboard_led.value() == 1 and time_since >= 500:
        onboard_led.toggle()
        last_blink = ticks_ms()


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
sign_of_life(True)

while True:
    client.check_msg()
    heartbeat(False)
    sign_of_life(False)
