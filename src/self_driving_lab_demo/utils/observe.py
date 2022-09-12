"""Based on the following resource:
https://www.steves-internet-guide.com/receiving-messages-mqtt-python-clientq=Queue() # noqa: E501
"""
import ast
import json
import logging
import sys
from ast import literal_eval
from queue import Queue
from uuid import uuid4

import paho.mqtt.client as mqtt
import requests
import serial

from self_driving_lab_demo.utils.channel_info import CHANNEL_NAMES

sensor_data_queue: "Queue[dict]" = Queue()
timeout = 30

_logger = logging.getLogger(__name__)


def on_message(client, userdata, msg):
    sensor_data_queue.put(json.loads(msg.payload))


def mqtt_observe_sensor_data(
    R, G, B, pico_id=None, session_id=None, hostname="test.mosquitto.org"
):
    if pico_id is None:
        _logger.warning(
            "No pico_id provided, but should be provided. On Pico, run the following to get your pico_id. from machine import unique_id; from ubinascii import hexlify; print(hexlify(unique_id()).decode()). Or change pico_id to whatever you want, but make it match between the Pico main.py and this mqtt_observe_sensor_data kwarg."  # noqa: E501
        )
    if session_id is None:
        session_id = str(uuid4())

    experiment_id = str(uuid4())

    prefix = f"sdl-demo/picow/{pico_id}/"
    neopixel_topic = prefix + "GPIO/28"
    sensor_topic = prefix + "as7341/"

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(sensor_topic, qos=1)

    client = mqtt.Client()  # create new instance
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(hostname)  # connect to broker
    client.subscribe(sensor_topic, qos=1)

    # ensures double quotes for JSON compatiblity
    payload = json.dumps(
        dict(
            R=int(R),
            G=int(G),
            B=int(B),
            _session_id=session_id,
            _experiment_id=experiment_id,
        )
    )
    client.publish(neopixel_topic, payload, qos=2)

    client.loop_start()
    while True:
        sensor_data = sensor_data_queue.get(timeout)
        inp = sensor_data["_input_message"]
        if inp["_session_id"] == session_id and inp["_experiment_id"] == experiment_id:
            assert inp["R"] == R, "red value mismatch"
            assert inp["G"] == G, "green value mismatch"
            assert inp["B"] == B, "blue value mismatch"
            client.loop_stop()
            sensor_data.pop("_input_message")  # remove the input message
            return sensor_data


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


def nonwireless_pico_observe_sensor_data(R, G, B, astep=100, atime=999, com=None):

    # If on Windows, might not be COM3, check device manager --> Ports
    # https://www.tomshardware.com/how-to/detect-com-port-windows-serial-port-notifier
    # or take a look at the bottom-RHS of Thonny when connected to the RPi
    if com is None:
        com = "COM3" if "win" in sys.platform else "/dev/ttyACM0"

    s = serial.Serial(com, 115200)

    def set_color(red, green, blue):
        s.write(f"set_color({red}, {green}, {blue})\n".encode("utf-8"))

    def read_sensor(astep=100, atime=999):
        s.write(f"read_sensor({astep}, {atime})\n".encode("utf-8"))
        sensor_data_str = s.readline().strip().decode("utf-8")
        s.readline()  # get rid of the extra line
        if sensor_data_str == "":
            raise ValueError("No data returned")
        return literal_eval(sensor_data_str)

    set_color(R, G, B)
    sensor_data = read_sensor(astep=astep, atime=atime)
    return {channel: datum for channel, datum in zip(CHANNEL_NAMES, sensor_data)}


# %% Code Graveyard

# t = time()
# while sensor_data_queue.empty():
#     client.loop()
#     if t - time() > 30:
#         raise ValueError("Failed to retrieve message within timeout period")
