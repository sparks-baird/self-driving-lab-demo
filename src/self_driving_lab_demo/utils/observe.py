"""Based on the following resource:
https://www.steves-internet-guide.com/receiving-messages-mqtt-python-clientq=Queue() # noqa: E501
"""
import ast
import json
import logging
import sys
from ast import literal_eval
from queue import Empty, Queue

# from ray.util.queue import Queue
from time import time
from uuid import uuid4

import numpy as np
import paho.mqtt.client as mqtt
import requests
import serial

from self_driving_lab_demo.utils.channel_info import CHANNEL_NAMES

_logger = logging.getLogger(__name__)

sensor_data_queue: "Queue[dict]" = Queue()


def mqtt_observe_sensor_data(
    R: int,
    G: int,
    B: int,
    atime: int = 100,
    astep: int = 999,
    gain: int = 128,
    pico_id=None,
    session_id=None,
    timeout=3600,
    queue_timeout=60,
    hostname="test.mosquitto.org",
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

    def on_message(client, userdata, msg):
        sensor_data_queue.put(json.loads(msg.payload))

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(sensor_topic, qos=1)

    # NOTE: don't pass client_id=session_id, otherwise you might run into issues with
    # running multiple experiments simultaneously with overlapping client_id-s
    client = mqtt.Client()  # create new instance
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(hostname)  # connect to broker
    client.subscribe(sensor_topic, qos=1)

    assert 0 <= atime <= 255, f"atime ({atime}) should be between 0 and 255"
    assert 0 <= astep <= 65534, f"astep ({astep}) should be between 0 and 65534"
    assert 0.5 <= gain <= 512, f"gain ({gain}) should be between 0.5 and 512"

    integration_time = (astep + 1) * (atime + 1) * 2.78 / 1000  # as7341.py

    # ensures double quotes for JSON compatiblity
    payload = json.dumps(
        dict(
            R=int(np.round(R)),
            G=int(np.round(G)),
            B=int(np.round(B)),
            atime=int(np.round(atime)),
            astep=int(np.round(astep)),
            integration_time=integration_time,
            gain=int(np.round(gain)),
            _session_id=session_id,
            _experiment_id=experiment_id,
        )
    )
    client.publish(neopixel_topic, payload, qos=2)

    client.loop_start()
    t0 = time()
    while True:
        if time() - t0 > timeout:
            raise ValueError(f"Sensor data retrieval timed out ({timeout} seconds)")
        sensor_data = sensor_data_queue.get(True, queue_timeout)
        inp = sensor_data["_input_message"]

        if (
            isinstance(inp, dict)
            and inp["_session_id"] == session_id
            and inp["_experiment_id"] == experiment_id
        ):
            if sensor_data.get("error", None) is not None:
                raise ValueError(
                    f"Experiment failed. {sensor_data['error']}. Input message: {inp}"
                )

            # input checking
            assert inp["R"] == R, f"red value mismatch {inp['R']} != {R}"
            assert inp["G"] == G, f"green value mismatch {inp['G']} != {G}"
            assert inp["B"] == B, f"blue value mismatch {inp['B']} != {B}"
            assert (
                inp["atime"] == atime
            ), f"atime value mismatch {inp['atime']} != {atime}"
            assert (
                inp["astep"] == astep
            ), f"astep value mismatch {inp['astep']} != {astep}"
            assert inp["gain"] == gain, f"gain value mismatch {inp['gain']} != {gain}"

            client.loop_stop()
            sensor_data.pop("_input_message")  # remove the input message
            return sensor_data
        # except Empty:
        #     pass


def liquid_observe_sensor_data(
    R: float,
    Y: float,
    B: float,
    water: float = 0.0,
    prerinse_time: float = 5.0,
    atime: int = 100,
    astep: int = 999,
    gain: int = 128,
    pico_id=None,
    session_id=None,
    timeout=3600,
    queue_timeout=60,
    hostname="test.mosquitto.org",
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

    def on_message(client, userdata, msg):
        sensor_data_queue.put(json.loads(msg.payload))

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(sensor_topic, qos=1)

    # NOTE: don't pass client_id=session_id, otherwise you might run into issues with
    # running multiple experiments simultaneously with overlapping client_id-s
    client = mqtt.Client()  # create new instance
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(hostname)  # connect to broker
    client.subscribe(sensor_topic, qos=1)

    assert 0 <= atime <= 255, f"atime ({atime}) should be between 0 and 255"
    assert 0 <= astep <= 65534, f"astep ({astep}) should be between 0 and 65534"
    assert 0.5 <= gain <= 512, f"gain ({gain}) should be between 0.5 and 512"

    integration_time = (astep + 1) * (atime + 1) * 2.78 / 1000  # as7341.py

    # ensures double quotes for JSON compatiblity
    payload = json.dumps(
        dict(
            R=float(R),
            Y=float(Y),
            B=float(B),
            water=float(water),
            prerinse_time=float(prerinse_time),
            atime=int(np.round(atime)),
            astep=int(np.round(astep)),
            integration_time=integration_time,
            gain=int(np.round(gain)),
            _session_id=session_id,
            _experiment_id=experiment_id,
        )
    )
    client.publish(neopixel_topic, payload, qos=2)

    client.loop_start()
    t0 = time()
    while True:
        if time() - t0 > timeout:
            raise Empty(f"Sensor data retrieval timed out ({timeout} seconds)")

        try:
            sensor_data = sensor_data_queue.get(True, queue_timeout)
        except Empty as e:
            raise Empty(
                "Sensor data retrieval timed out ({queue_timeout} seconds)"
            ) from e
        inp = sensor_data["_input_message"]

        if (
            isinstance(inp, dict)
            and inp["_session_id"] == session_id
            and inp["_experiment_id"] == experiment_id
        ):
            if sensor_data.get("error", None) is not None:
                raise ValueError(
                    f"Experiment failed. {sensor_data['error']}. Input message: {inp}"
                )

            # input checking
            assert inp["R"] == R, f"red value mismatch {inp['R']} != {R}"
            assert inp["Y"] == Y, f"green value mismatch {inp['Y']} != {Y}"
            assert inp["B"] == B, f"blue value mismatch {inp['B']} != {B}"
            assert (
                inp["water"] == water
            ), f"water value mismatch {inp['water']} != {water}"
            assert (
                inp["prerinse_time"] == prerinse_time
            ), f"prerinse_time value mismatch {inp['prerinse_time']} != {prerinse_time}"
            assert (
                inp["atime"] == atime
            ), f"atime value mismatch {inp['atime']} != {atime}"
            assert (
                inp["astep"] == astep
            ), f"astep value mismatch {inp['astep']} != {astep}"
            assert inp["gain"] == gain, f"gain value mismatch {inp['gain']} != {gain}"

            client.loop_stop()
            sensor_data.pop("_input_message")  # remove the input message
            return sensor_data


def pico_server_observe_sensor_data(
    R: int,
    G: int,
    B: int,
    atime: int = 100,
    astep: int = 999,
    gain: int = 128,
    url="http://192.168.0.111/",
):
    payload = {
        "control_led": "Send+command+to+LED",
        "red": str(R),
        "green": str(G),
        "blue": str(B),
        "atime": str(atime),
        "astep": str(astep),
        "gain": str(gain),
    }
    r = requests.post(url, data=payload)
    sensor_data_cookie = r.cookies["sensor_data"]
    return ast.literal_eval(sensor_data_cookie)


def nonwireless_pico_observe_sensor_data(
    R, G, B, astep=100, atime=999, gain=128, com=None
):

    # If on Windows, might not be COM3, check device manager --> Ports
    # https://www.tomshardware.com/how-to/detect-com-port-windows-serial-port-notifier
    # or take a look at the bottom-RHS of Thonny when connected to the RPi
    if com is None:
        com = "COM3" if "win" in sys.platform else "/dev/ttyACM0"

    s = serial.Serial(com, 115200)

    def set_color(red, green, blue):
        s.write(f"set_color({red}, {green}, {blue})\n".encode("utf-8"))

    def read_sensor(astep=100, atime=999):
        s.write(f"read_sensor({astep}, {atime}, {gain})\n".encode("utf-8"))
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

# sensor_data = sensor_data_queue.get(False)

# sensor_data = {
#     "ch470": 4390,
#     "ch670": 2044,
#     "ch550": 1287,
#     "ch410": 613,
#     "ch440": 2378,
#     "_input_message": {
#         "_session_id": session_id,
#         "R": R,
#         "G": G,
#         "B": B,
#         "_experiment_id": experiment_id,
#         "atime": atime,
#         "astep": astep,
#         "gain": gain,
#     },
#     "ch583": 1252,
#     "ch510": 1441,
#     "ch620": 1490,
# }
