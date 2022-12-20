"""Run a self-driving lab on a Raspberry Pi Pico W."""
import json
import os
from secrets import HIVEMQ_HOST, HIVEMQ_PASSWORD, HIVEMQ_USERNAME, PASSWORD, SSID
from time import sleep

import ntptime
import ussl
from as7341_sensor import Sensor
from data_logging import initialize_sdcard
from machine import PWM, Pin, unique_id
from neopixel import NeoPixel
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
from umqtt.robust import MQTTClient

try:
    from secrets import (
        DEVICE_NICKNAME,
        MONGODB_API_KEY,
        MONGODB_APP_NAME,
        MONGODB_CLUSTER_NAME,
        MONGODB_COLLECTION_NAME,
        MONGODB_DATABASE_NAME,
    )
except Exception as e:
    print(get_traceback(e))

port = 8883

logfile = open("log.txt", "a")
# duplicate stdout and stderr to the log file
os.dupterm(logfile)

# https://medium.com/@johnlpage/introduction-to-microcontrollers-and-the-pi-pico-w-f7a2d9ad1394
# you can request a MongoDB collection specific to you by emailing
# sterling.baird@utah.edu
mongodb_url = f"https://data.mongodb-api.com/app/{MONGODB_APP_NAME}/endpoint/data/v1/action/insertOne"  # noqa: E501

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

# at minimum, the following functions should be defined:
# - run_experiment (use a parameters dict to run experiment and return sensor data)
# - initialize_devices (return dict mapping device name --> device object or empty dict)
# - reset_experiment (reset experiment to initial state)
# - emergency_shutdown (can be same as reset_experiment if needed)

# device objects should be defined here
pixels = NeoPixel(Pin(28), 1)  # one NeoPixel on Pin 28 (GP28)
sensor = Sensor()


def get_devices():
    # enforce instantiation of the devices a single time (i.e. singleton function)
    return {"pixels": pixels, "sensor": sensor}


def run_experiment(parameters, devices=None):
    if devices is None:
        devices = get_devices()

    pixels = devices["pixels"]
    sensor = devices["sensor"]

    r, g, b = [parameters[key] for key in ["R", "G", "B"]]
    atime = parameters.get("atime", 100)
    astep = parameters.get("astep", 999)
    gain = parameters.get("gain", 128)

    assert 0 <= r <= 255, f"Invalid R: {r} (must be between 0 and 255)"
    assert 0 <= g <= 255, f"Invalid G: {g} (must be between 0 and 255)"
    assert 0 <= b <= 255, f"Invalid B: {b} (must be between 0 and 255)"
    assert 0 <= atime <= 255, f"Invalid atime: {atime} (must be between 0 and 255)"
    assert 0 <= astep <= 65536, f"Invalid astep: {astep} (must be between 0 and 65536)"
    assert 0.5 <= gain <= 512, f"Invalid gain: {gain} (must be between 0.5 and 512)"

    pixels[0] = (r, g, b)
    pixels.write()

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


def reset_experiment(parameters, devices=None):
    if devices is None:
        devices = get_devices()

    pixels = devices["pixels"]

    # Turn off the LED
    pixels[0] = (0, 0, 0)
    pixels.write()


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
            cluster_name=MONGODB_CLUSTER_NAME,
            database_name=MONGODB_DATABASE_NAME,
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
        client.check_msg()
        heartbeat(client, False)
        sign_of_life(onboard_led, False)
