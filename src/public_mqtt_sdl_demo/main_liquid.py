"""Run a materials acceleration platform demo on a Raspberry Pi Pico W."""
import json
import os
from secrets import HIVEMQ_HOST, HIVEMQ_PASSWORD, HIVEMQ_USERNAME, PASSWORD, SSID
from time import sleep, ticks_diff, ticks_ms

import ntptime
import ussl
from as7341_sensor import Sensor
from data_logging import initialize_sdcard
from machine import PWM, Pin, unique_id
from netman import connectWiFi
from sdl_demo_utils import (
    Experiment,
    encrypt_id,
    get_onboard_led,
    get_traceback,
    heartbeat,
    sign_of_life,
)
from ubinascii import hexlify
from umqtt.simple import MQTTClient

try:
    from secrets import DEVICE_NICKNAME, MONGODB_API_KEY, MONGODB_COLLECTION_NAME
except Exception as e:
    print(get_traceback(e))

port = 8883

# https://medium.com/@johnlpage/introduction-to-microcontrollers-and-the-pi-pico-w-f7a2d9ad1394
# you can request a MongoDB collection specific to you by emailing
# sterling.baird@utah.edu
mongodb_app_name = "data-sarkl"
mongodb_url = f"https://data.mongodb-api.com/app/{mongodb_app_name}/endpoint/data/v1/action/insertOne"  # noqa: E501
mongodb_cluster_name = "sparks-materials-informatics"
mongodb_database_name = "clslab-liquid-mixing"

my_id = hexlify(unique_id()).decode()
my_encrypted_id = encrypt_id(my_id, verbose=True)

# # aside: for sgbaird's public test demo only
# my_id = "test"
# my_encrypted_id = "test"

trunc_device_id = str(my_encrypted_id)[0:10]
prefix = f"sdl-demo/picow/{my_id}/"

print(f"Unencrypted PICO ID (keep private): {my_id}")
print(f"Encrypted PICO ID (OK to share publicly): {my_encrypted_id}")
print(f"Truncated, encrypted PICO ID (OK to share publicly): {trunc_device_id}")
print(f"MQTT prefix: {prefix}")

connectWiFi(SSID, PASSWORD, country="US")

sdcard_backup_fpath = "/sd/experiments.txt"

# To validate certificates, a valid time is required
ntptime.timeout = 5  # type: ignore
ntptime.host = "de.pool.ntp.org"
ntptime.settime()

print("Obtaining CA Certificate")
with open("hivemq-com-chain.der", "rb") as f:
    cacert = f.read()
f.close()

######################################
#### BEGIN USER-DEFINED FUNCTIONS ####
######################################

PUMP_PINS = {"R": 0, "Y": 1, "B": 2, "water": 3}
pumps = {name: PWM(Pin(i)) for name, i in PUMP_PINS.items()}
white_led = Pin(9, mode=Pin.OUT)
sensor = Sensor()


def get_devices():
    return {"pumps": pumps, "sensor": sensor, "white_led": white_led}


def validate_inputs(parameters, devices=None):
    pass


def run_pump(pump, power):
    pump.freq(20000)
    pump.duty_u16(round(65535 * power))


def run_pumps(pumps, powers, runtime):
    runtime_ms = runtime * 1000
    t0 = ticks_ms()

    for pump, power in zip(pumps, powers):
        pump.freq(20000)
        pump.duty_u16(int(round(65535 * power)))

    while True:
        if ticks_diff(ticks_ms(), t0) > runtime_ms:
            break
        sleep(0.01)


def control_inputs(parameters, devices=None):
    if devices is None:
        devices = get_devices()

    # USER-DEFINED
    pumps = devices["pumps"]
    water_pump = pumps["water"]

    # REVIEW: probably better to rinse at beginning of experiment than end
    prerinse_power = parameters.get("prerinse_power", 0.5)
    prerinse_time = parameters.get("prerinse_time", 5.0)
    run_pump(water_pump, prerinse_power)
    sleep(prerinse_time)

    runtime = parameters.get("runtime", 5.0)
    keys = list(pumps.keys())
    run_pumps(
        [pumps[key] for key in keys],
        [parameters[key] for key in keys],
        runtime,
    )

    # REVIEW: if a flow sensor were installed in the waste, this could be used
    # to verify that the experiment is functioning properly. If the flow doesn't
    # match what's expected based on the input parameters, then an error could
    # be raised and an email notification, indicating a need for maintenance.


def measure_sensors(parameters, devices=None):
    if devices is None:
        devices = get_devices()

    white_led = devices["white_led"]
    sensor = devices["sensor"]
    white_led.on()

    atime = parameters.get("atime", 100)
    astep = parameters.get("astep", 999)
    gain = parameters.get("gain", 128)

    sensor._atime = atime
    sensor._astep = astep
    sensor._gain = gain
    sensor_data = sensor.all_channels

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

    sensor_data = {ch: datum for ch, datum in zip(CHANNEL_NAMES, sensor_data)}
    return sensor_data


def run_experiment(parameters, devices=None):
    control_inputs(parameters, devices=devices)
    sensor_data = measure_sensors(parameters, devices=devices)
    return sensor_data


def reset_experiment(parameters, devices=None):
    if devices is None:
        devices = get_devices()

    pumps = devices["pumps"]
    white_led = devices["white_led"]

    white_led.off()

    # Turn off the pumps
    [run_pump(pump, 0.0) for pump in pumps.values()]


def emergency_shutdown(devices=None):
    # in CLSLabs:Liquid case, same as reset_experiment
    if devices is None:
        devices = get_devices()

    pumps = devices["pumps"]
    white_led = devices["white_led"]

    white_led.off()

    # Turn off the pumps
    [run_pump(pump, 0.0) for pump in pumps.values()]


######################################
##### END USER-DEFINED FUNCTIONS #####
######################################

devices = get_devices()

onboard_led = get_onboard_led()
buzzer = PWM(Pin(18))
sdcard_ready = initialize_sdcard()


# MQTT Resources:
# https://gist.github.com/sammachin/b67cc4f395265bccd9b2da5972663e6d
# http://www.steves-internet-guide.com/into-mqtt-python-client/

experiment = Experiment(
    run_experiment_fn=run_experiment,
    reset_experiment_fn=reset_experiment,
    emergency_shutdown_fn=reset_experiment,
    devices=devices,
    buzzer=buzzer,
    sdcard_ready=sdcard_ready,
)


def callback(topic, msg, retain=None, dup=None):
    t = topic.decode("utf-8").lstrip(prefix)
    print(t)

    if t[:5] == "GPIO/":
        payload_data = experiment.try_experiment(msg)

        payload = json.dumps(payload_data)
        print(payload)

        if experiment.sdcard_ready:
            payload = experiment.write_to_sd_card(payload, fpath=sdcard_backup_fpath)

        # prefer qos=1, but causes recursion error if too many messages in short period
        # of time
        client.publish(prefix + "as7341/", payload, qos=0)

        experiment.log_to_mongodb(
            payload_data,
            url=mongodb_url,
            api_key=MONGODB_API_KEY,
            cluster_name=mongodb_cluster_name,
            database_name=mongodb_database_name,
            collection_name=MONGODB_COLLECTION_NAME,
            device_nickname=DEVICE_NICKNAME,
            trunc_device_id=trunc_device_id,
            verbose=True,
            retries=2,
        )


client = MQTTClient(
    prefix,
    HIVEMQ_HOST,
    user=HIVEMQ_USERNAME,
    password=HIVEMQ_PASSWORD,
    keepalive=30,
    ssl=True,
    ssl_params={
        "server_side": False,
        "key": None,
        "cert": None,
        "cert_reqs": ussl.CERT_REQUIRED,
        "cadata": cacert,
        "server_hostname": HIVEMQ_HOST,
    },
)
del cacert
try:
    client.connect()
except OSError as e:
    print(get_traceback(e))
    print("Retrying client.connect() in 2 seconds...")
    sleep(2.0)
    client.connect()

client.set_callback(callback)
client.subscribe(prefix + "GPIO/#")

heartbeat(client, True)
sign_of_life(onboard_led, True)

print("Waiting for experiment requests...")

while True:
    try:
        client.check_msg()
        heartbeat(client, False)
        sign_of_life(onboard_led, False)
    except Exception as e:
        logfile = open("log.txt", "w")
        # duplicate stdout and stderr to the log file
        os.dupterm(logfile)
        client.check_msg()
        heartbeat(client, False)
        sign_of_life(onboard_led, False)


# %% Code Graveyard

# def validate_inputs(parameters, devices=None):
#     # don't allow access to hardware if any input values are out of bounds
#     r, y, b, w = [parameters[key] for key in ["R", "Y", "B", "water"]]
#     runtime = parameters.get("runtime", 5.0)
#     prerinse_power = parameters.get("prerinse_power", 0.5)
#     prerinse_time = parameters.get("prerinse_time", 5.0)

#     atime = parameters.get("atime", 100)
#     astep = parameters.get("astep", 999)
#     gain = parameters.get("gain", 128)

#     assert 0 <= r <= 1, f"R must be between 0 and 1, not {r}"
#     assert 0 <= y <= 1, f"Y must be between 0 and 1, not {y}"
#     assert 0 <= b <= 1, f"B must be between 0 and 1, not {b}"
#     assert 0 <= w <= 1, f"water must be between 0 and 1, not {w}"
#     assert 0 <= runtime <= 5, f"runtime must be between 0 and 20, not {runtime}"
#     assert (
#         0 <= prerinse_power <= 1
#     ), f"prerinse_power must be between 0 and 1, not {prerinse_power}"  # noqa: E501
#     assert (
#         0 <= prerinse_time <= 5
#     ), f"prerinse_time must be between 0 and 20, not {prerinse_time}"  # noqa: E501
#     assert 0 <= atime <= 255, f"Invalid atime: {atime} (must be between 0 and 255)"
#     assert 0 <= astep <= 65536, f"Invalid astep: {astep} (must be between 0 and 65536)"
#     assert 0.5 <= gain <= 512, f"Invalid gain: {gain} (must be between 0.5 and 512)"

#     if not isinstance(r, float):
#         raise ValueError(f"R must be a float, not {type(r)} ({r})")

#     if not isinstance(y, float):
#         raise ValueError(f"Y must be a float, not {type(y)} ({y})")

#     if not isinstance(b, float):
#         raise ValueError(f"B must be a float, not {type(b)} ({b})")

#     if not isinstance(w, float):
#         raise ValueError(f"water must be a float, not {type(w)} ({w})")

#     if not isinstance(atime, int):
#         raise ValueError(f"atime must be an integer, not {type(atime)} ({atime})")

#     if not isinstance(astep, int):
#         raise ValueError(f"astep must be an integer, not {type(astep)} ({astep})")

#     if not isinstance(gain, int) and gain != 0.5:
#         if gain not in [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512]:
#             raise ValueError(f"gain must be an integer, not {type(gain)} ({gain})")

#     if not isinstance(runtime, float):
#         raise ValueError(f"runtime must be a float, not {type(runtime)} ({runtime})")

#     if not isinstance(prerinse_time, float):
#         raise ValueError(
#             f"prerinse_time must be a float, not {type(prerinse_time)} ({prerinse_time})"
#         )


# def validate_inputs(parameters, devices=None):
#     # don't allow access to hardware if any input values are out of bounds
#     r, y, b, w = [parameters[key] for key in ["R", "Y", "B", "water"]]
#     runtime = parameters.get("runtime", 5.0)
#     prerinse_power = parameters.get("prerinse_power", 0.5)
#     prerinse_time = parameters.get("prerinse_time", 5.0)

#     atime = parameters.get("atime", 100)
#     astep = parameters.get("astep", 999)
#     gain = parameters.get("gain", 128)

#     assert 0 <= r <= 1, f"R must be between 0 and 1, not {r}"
#     assert 0 <= y <= 1, f"Y must be between 0 and 1, not {y}"
#     assert 0 <= b <= 1, f"B must be between 0 and 1, not {b}"
#     assert 0 <= w <= 1, f"water must be between 0 and 1, not {w}"
#     assert 0 <= runtime <= 5, f"runtime must be between 0 and 20, not {runtime}"
#     assert (
#         0 <= prerinse_power <= 1
#     ), f"prerinse_power must be between 0 and 1, not {prerinse_power}"  # noqa: E501
#     assert (
#         0 <= prerinse_time <= 5
#     ), f"prerinse_time must be between 0 and 20, not {prerinse_time}"  # noqa: E501
#     assert 0 <= atime <= 255, f"Invalid atime: {atime} (must be between 0 and 255)"
#     assert 0 <= astep <= 65536, f"Invalid astep: {astep} (must be between 0 and 65536)"
#     assert 0.5 <= gain <= 512, f"Invalid gain: {gain} (must be between 0.5 and 512)"
