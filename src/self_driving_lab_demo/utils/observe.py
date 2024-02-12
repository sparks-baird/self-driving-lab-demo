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
from typing import Optional, Union
from uuid import uuid4

import numpy as np
import paho.mqtt.client as paho
import requests
import serial
from paho import mqtt

from self_driving_lab_demo.utils.channel_info import CHANNEL_NAMES

_logger = logging.getLogger(__name__)

sensor_data_queue: "Queue[dict]" = Queue()


def mqtt_observe_sensor_data(
    R: int,
    G: int,
    B: int,
    atime: int = 100,
    astep: int = 999,
    gain: Union[int, float] = 128,
    pico_id: Optional[str] = None,
    session_id: Optional[str] = None,
    timeout: int = 3600,
    queue_timeout: int = 60,
    client=None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    hostname=None,
    port=8883,
    tls=True,
    mongodb=True,
    extra_info: Optional[dict] = None,
):
    if pico_id is None:
        # _logger.warning(
        raise ValueError(
            "No pico_id provided, but should be provided. On Pico, run the following to get your pico_id. from machine import unique_id; from ubinascii import hexlify; print(hexlify(unique_id()).decode()). Or change pico_id to whatever you want, but make it match between the Pico main.py and this mqtt_observe_sensor_data kwarg."  # noqa: E501
        )
    if session_id is None:
        session_id = str(uuid4())

    experiment_id = str(uuid4())

    prefix = f"sdl-demo/picow/{pico_id}/"
    neopixel_topic = prefix + "GPIO/28"
    sensor_topic = prefix + "as7341/"

    # NOTE: don't pass client_id=session_id, otherwise you might run into issues with
    # running multiple experiments simultaneously with overlapping client_id-s
    if client is None:
        client = get_paho_client(
            sensor_topic,
            username=username,
            password=password,
            hostname=hostname,
            port=port,
            tls=tls,
        )

    assert 0 <= atime <= 255, f"atime ({atime}) should be between 0 and 255"
    assert 0 <= astep <= 65534, f"astep ({astep}) should be between 0 and 65534"
    assert 0.5 <= gain <= 512, f"gain ({gain}) should be between 0.5 and 512"

    integration_time_s = (astep + 1) * (atime + 1) * 2.78 / 1e6  # as7341.py

    payload_data = dict(
        R=int(np.round(R)),
        G=int(np.round(G)),
        B=int(np.round(B)),
        atime=int(np.round(atime)),
        astep=int(np.round(astep)),
        integration_time_s=integration_time_s,
        gain=float(gain),
        mongodb=mongodb,
        _session_id=session_id,
        _experiment_id=experiment_id,
    )
    if extra_info is not None:
        payload_data["extra_info"] = extra_info  # type: ignore
    # ensures double quotes for JSON compatiblity
    payload = json.dumps(payload_data)
    client.publish(neopixel_topic, payload, qos=2)

    client.loop_start()
    t0 = time()
    while True:
        if time() - t0 > timeout:
            raise ValueError(f"Sensor data retrieval timed out ({timeout} seconds)")
        try:
            sensor_data = sensor_data_queue.get(True, queue_timeout)
        except Empty as e:
            raise Empty(
                f"Sensor data retrieval timed out ({queue_timeout} seconds)"
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


def get_paho_client(
    sensor_topic, username=None, password=None, hostname=None, port=8883, tls=True
):
    if username is None:
        username = "sgbaird"
    if password is None:
        password = "D.Pq5gYtejYbU#L"
    if hostname is None:
        hostname = "248cc294c37642359297f75b7b023374.s2.eu.hivemq.cloud"

    client = paho.Client(
        paho.CallbackAPIVersion.VERSION1, protocol=paho.MQTTv5
    )  # create new instance

    def on_message(client, userdata, msg):
        sensor_data_queue.put(json.loads(msg.payload))

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc != 0:
            print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(sensor_topic, qos=1)

    client.on_connect = on_connect
    client.on_message = on_message

    # enable TLS for secure connection
    if tls:
        client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(hostname, port)
    client.subscribe(sensor_topic, qos=1)
    return client


def liquid_observe_sensor_data(
    R: float,
    Y: float,
    B: float,
    water: float = 0.0,
    prerinse_power: float = 0.5,
    prerinse_time: float = 20.0,
    runtime: float = 10.0,
    atime: int = 100,
    astep: int = 999,
    gain: Union[int, float] = 128,
    pico_id=None,
    session_id=None,
    timeout=3600,
    queue_timeout=60,
    client=None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    hostname=None,
    port=8883,
    tls=True,
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

    # NOTE: don't pass client_id=session_id, otherwise you might run into issues with
    # running multiple experiments simultaneously with overlapping client_id-s
    if client is None:
        client = get_paho_client(
            sensor_topic,
            username=username,
            password=password,
            hostname=hostname,
            port=port,
            tls=tls,
        )

    assert 0 <= atime <= 255, f"atime ({atime}) should be between 0 and 255"
    assert 0 <= astep <= 65534, f"astep ({astep}) should be between 0 and 65534"
    assert 0.5 <= gain <= 512, f"gain ({gain}) should be between 0.5 and 512"

    integration_time_s = (astep + 1) * (atime + 1) * 2.78 / 1e6  # as7341.py

    # ensures double quotes for JSON compatiblity
    payload = json.dumps(
        dict(
            R=float(R),
            Y=float(Y),
            B=float(B),
            water=float(water),
            prerinse_power=float(prerinse_power),
            prerinse_time=float(prerinse_time),
            runtime=float(runtime),
            atime=int(np.round(atime)),
            astep=int(np.round(astep)),
            integration_time_s=integration_time_s,
            gain=float(gain),
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
                f"Sensor data retrieval timed out ({queue_timeout} seconds)"
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
            assert round(inp["R"], 4) == round(
                R, 4
            ), f"red value mismatch {inp['R']} != {R}"
            assert round(inp["Y"], 4) == round(
                Y, 4
            ), f"green value mismatch {inp['Y']} != {Y}"
            assert round(inp["B"], 4) == round(
                B, 4
            ), f"blue value mismatch {inp['B']} != {B}"
            assert round(inp["water"], 4) == round(
                water, 4
            ), f"water value mismatch {inp['water']} != {water}"
            assert round(inp["prerinse_power"], 4) == round(
                prerinse_power, 4
            ), f"prerinse_power value mismatch {inp['prerinse_power']} != {prerinse_power}"  # noqa: E501
            assert round(inp["prerinse_time"], 4) == round(
                prerinse_time, 4
            ), f"prerinse_time value mismatch {inp['prerinse_time']} != {prerinse_time}"
            assert round(inp["runtime"], 4) == round(
                runtime, 4
            ), f"runtime value mismatch {inp['runtime']} != {runtime}"
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


def liquid_dummy_observe_sensor_data(R, Y, B, **kwargs):
    # return a fixed set of values (no interaction with real hardware)
    return {
        "utc_timestamp": 1671675884,
        "background": {
            "ch470": 21288,
            "ch410": 5835,
            "ch440": 65535,
            "ch510": 21632,
            "ch550": 6760,
            "ch670": 8970,
            "ch620": 2901,
            "ch583": 2057,
        },
        "ch470": 21288,
        "ch410": 5835,
        "ch440": 65535,
        "sd_card_ready": False,
        "ch510": 21632,
        "ch550": 6760,
        "ch670": 8970,
        "utc_time_str": "2022-12-22 02:24:44",
        "onboard_temperature_K": 297.8537,
        "ch620": 2901,
        "ch583": 2057,
    }


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

# if (
#     port is None
#     and username is None
#     and password is None
#     and hostname == "broker.hivemq.com"
# ):
#     tls = False
#     port = 1883
# elif port is None and tls is None:
#     port = 8883
#     tls = True
# else:
#     raise (ValueError("Invalid port and tls combination"))
