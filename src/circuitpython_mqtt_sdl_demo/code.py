"""
Based on https://gist.github.com/sammachin/b67cc4f395265bccd9b2da5972663e6d
http://www.steves-internet-guide.com/into-mqtt-python-client/
"""
import json
from binascii import hexlify
from secrets import secrets
from time import sleep

import board
import busio
import digitalio
import microcontroller
import neopixel
import socketpool
import wifi
from adafruit_as7341 import AS7341
from adafruit_minimqtt.adafruit_minimqtt import MQTT
from adafruit_ticks import ticks_diff, ticks_ms

SSID, PASSWORD = secrets["ssid"], secrets["password"]

BROKER = "test.mosquitto.org"

pool = socketpool.SocketPool(wifi.radio)

wifi.radio.connect(SSID, PASSWORD)

pixel_pin = board.GP28
num_pixels = 1

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.35, auto_write=False)

i2c = busio.I2C(sda=board.GP26, scl=board.GP27)  # see Maker Pi Pico Base pinout
sensor = AS7341(i2c)

uid = microcontroller.Processor.uid
my_id = hexlify(b"{uid}").decode()

prefix = f"sdl-demo/picow/{my_id}/"

print(f"prefix: {prefix}")

onboard_led = digitalio.DigitalInOut(board.LED)  # only works for Pico W
onboard_led.direction = digitalio.Direction.OUTPUT

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


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    # prefer qos=2, but not implemented
    client.subscribe(prefix + "GPIO/#", qos=0)


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

        sensor_data = sensor.all_channels

        # Turn off the LED
        pixels[0] = (0, 0, 0)
        pixels.write()

        sensor_data_dict = {}
        for ch, datum in zip(CHANNEL_NAMES, sensor_data):
            sensor_data_dict[ch] = datum

        sensor_data_dict["_input_message"] = data

        payload = json.dumps(sensor_data_dict)

        print(payload)

        # prefer qos=1, but causes recursion error if too many messages in short period
        # of time
        client.publish(prefix + "as7341/", payload, qos=0)


def heartbeat(first):
    global lastping
    if first:
        client.ping()
        lastping = ticks_ms()
    if ticks_diff(ticks_ms(), lastping) >= 300000:
        client.ping()
        lastping = ticks_ms()
    return


def toggle(onboard_led):
    if onboard_led.value:
        onboard_led.value = False
    else:
        onboard_led.value = True


def sign_of_life(first):
    global last_blink
    if first:
        onboard_led.value = True
        last_blink = ticks_ms()
    time_since = ticks_diff(ticks_ms(), last_blink)
    if onboard_led.value == False and time_since >= 5000:
        toggle(onboard_led)
        last_blink = ticks_ms()
    elif onboard_led.value == True and time_since >= 500:
        toggle(onboard_led)
        last_blink = ticks_ms()


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


def on_disconnect(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from MQTT Broker!")


# Set up a MiniMQTT Client
client = MQTT(
    client_id=prefix,
    broker=BROKER,
    username=None,
    password=None,
    is_ssl=False,
    port=1883,
    socket_pool=pool,
)

client.add_topic_callback(prefix + "GPIO/#", callback)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

client.connect()

client.subscribe(prefix + "GPIO/#")

heartbeat(True)
sign_of_life(True)

while True:
    sleep(2.0)
    client.loop(timeout=0.0)
    heartbeat(False)
    sign_of_life(False)


# %% Code Graveyard


# client = MQTTClient(
#     prefix,
#     "test.mosquitto.org",
#     user=None,
#     password=None,
#     keepalive=0,
#     ssl=False,
#     ssl_params={},
# )

# client.set_callback(callback)

# TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
# requests = adafruit_requests.Session(pool, None)
# with requests.get(TEXT_URL) as r:
#     print(f"{r.status_code} {r.reason.decode()} {r.content}")

# try:
#     onboard_led = Pin("LED", Pin.OUT)  # only works for Pico W
# except Exception as e:
#     print(e)
#     onboard_led = Pin(25, Pin.OUT)

# i2c = board.I2C()  # uses board.SCL and board.SDA
