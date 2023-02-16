"""
Based on https://gist.github.com/sammachin/b67cc4f395265bccd9b2da5972663e6d
http://www.steves-internet-guide.com/into-mqtt-python-client/
"""
import json
from binascii import hexlify
from secrets import secrets

import board
import digitalio
import microcontroller
import socketpool
import wifi
from adafruit_minimqtt.adafruit_minimqtt import MQTT

SSID, PASSWORD = secrets["ssid"], secrets["password"]

BROKER = "test.mosquitto.org"

TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"

pool = socketpool.SocketPool(wifi.radio)

wifi.radio.connect(SSID, PASSWORD)

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
    client.subscribe(prefix + "GPIO/#", qos=0)


def callback(topic, msg):
    t = topic.decode("utf-8").lstrip(prefix)
    print(t)

    if t[:5] == "GPIO/":
        p = int(t[5:])
        print(msg)
        data = json.loads(msg)
        onboard_led.value = data["value"]
        payload = {"onboard_led_value": onboard_led.value}
        print(payload)
        client.publish(prefix + "onboard_led/", payload, qos=0)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


# Set up a MiniMQTT Client
client = MQTT(
    client_id=prefix,
    broker=BROKER,
    username=None,
    password=None,
    is_ssl=False,
    socket_pool=pool,
)

client.add_topic_callback(prefix + "GPIO/#", callback)
client.on_connect = on_connect
client.on_message = on_message

client.connect()

client.subscribe(prefix + "GPIO/#")

# Start a blocking message loop...
# NOTE: NO code below this loop will execute
# NOTE: Network reconnection is handled within this loop
while True:
    try:
        client.loop()
    except Exception as e:
        pass
#     except (ValueError, RuntimeError) as e:
#         print("Failed to get data, retrying\n", e)
#         wifi.reset()
#         client.reconnect()
#         continue
