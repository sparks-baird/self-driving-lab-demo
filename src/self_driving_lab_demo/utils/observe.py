"""Based on the following resource:
https://www.steves-internet-guide.com/receiving-messages-mqtt-python-clientq=Queue() # noqa: E501
"""
import ast
import json
import logging
from queue import Queue
from time import time

import paho.mqtt.client as mqtt
import requests

sensor_data_queue = Queue()
timeout = 30

_logger = logging.getLogger(__name__)


def on_message(client, userdata, msg):
    sensor_data_queue.put(json.loads(msg.payload))


def mqtt_observe_sensor_data(R, G, B, pico_id=None, hostname="test.mosquitto.org"):
    if pico_id is None:
        _logger.warning(
            "No pico_id provided, but should be provided. On Pico, run the following to get your pico_id. from machine import unique_id; from ubinascii import hexlify; print(hexlify(unique_id()).decode()). Or change pico_id to whatever you want, but make it match between the Pico main.py and this mqtt_observe_sensor_data kwarg."  # noqa: E501
        )
    prefix = f"sdl-demo/picow/{pico_id}/"
    neopixel_topic = prefix + "GPIO/28"
    sensor_topic = prefix + "as7341/"

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(sensor_topic)

    client = mqtt.Client()  # create new instance
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(hostname)  # connect to broker
    client.subscribe(sensor_topic)

    # ensures double quotes for JSON compatiblity
    payload = json.dumps(dict(R=int(R), G=int(G), B=int(B)))
    client.publish(neopixel_topic, payload)

    t = time()
    while sensor_data_queue.empty():
        client.loop()
        if t - time() > 30:
            raise ValueError("Failed to retrieve message within timeout period")
    return sensor_data_queue.get()


def pico_server_observe_sensor_data(
    R: int, G: int, B: int, url="http://192.168.0.111/"
):
    payload = {
        "control_led": "Send+command+to+LED",
        "red": str(R),
        "green": str(G),
        "blue": str(B),
    }
    r = requests.post(url, data=payload)
    sensor_data_cookie = r.cookies["sensor_data"]
    return ast.literal_eval(sensor_data_cookie)
