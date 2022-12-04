"""
https://gist.github.com/sammachin/b67cc4f395265bccd9b2da5972663e6d
http://www.steves-internet-guide.com/into-mqtt-python-client/
"""

import json
from secrets import PASSWORD, SSID
from time import sleep, ticks_diff, ticks_ms  # type: ignore

import network
from as7341_sensor import Sensor
from data_logging import (
    get_onboard_temperature,
    get_timestamp,
    initialize_sdcard,
    log_to_mongodb,
    write_payload_backup,
)
from machine import PWM, Pin, unique_id
from neopixel import NeoPixel
from sdl_demo_utils import beep, get_traceback, merge_two_dicts
from ubinascii import hexlify
from ufastrsa.genprime import genrsa
from ufastrsa.rsa import RSA
from umqtt.simple import MQTTClient

my_id = hexlify(unique_id()).decode()

bits = 256  # use larger values for higher complexity (e.g. 512, 1028)
cipher = RSA(*genrsa(bits, e=65537))

prefix = f"sdl-demo/picow/{my_id}/"

print(f"prefix: {prefix}")

# https://medium.com/@johnlpage/introduction-to-microcontrollers-and-the-pi-pico-w-f7a2d9ad1394
# for a tutorial on how to use MongoDB Atlas with the Pico W, but you're welcome and
# encouraged to log to the public MongoDB instance via the information below :)
mongodb_app_name = "data-sarkl"
mongodb_url = f"https://data.mongodb-api.com/app/{mongodb_app_name}/endpoint/data/v1/action/insertOne"  # noqa: E501
mongodb_api_key = "KM4Y2EvuCeBsyOxVt6NYzLInNQOVBjZgpR9bIbUT2uCMINaQDIQk787iRx61Lt9X"
mongodb_cluster_name = "sparks-materials-informatics"
mongodb_database_name = "clslab-light-mixing"
mongodb_collection_name = "public"

data_backup_fpath = "/sd/experiments.txt"

try:
    onboard_led = Pin("LED", Pin.OUT)  # only works for Pico W
except Exception as e:
    print(e)
    onboard_led = Pin(25, Pin.OUT)

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

buzzer = PWM(Pin(18))

sdcard_ready = initialize_sdcard()


def initialize_devices():
    pixels = NeoPixel(Pin(28), 1)  # one NeoPixel on Pin 28 (GP28)
    sensor = Sensor()
    return {"pixels": pixels, "sensor": sensor}


devices = initialize_devices()


def validate_inputs(parameters, devices=None):
    # don't allow access to hardware if any input values are out of bounds

    # USER-DEFINED
    r, g, b = [parameters[key] for key in ["R", "G", "B"]]
    atime = parameters.get("atime", 100)
    astep = parameters.get("astep", 999)
    gain = parameters.get("gain", 128)

    if not isinstance(r, int):
        raise ValueError(f"R must be an integer, not {type(r)} ({r})")
    if not isinstance(g, int):
        raise ValueError(f"G must be an integer, not {type(g)} ({g})")
    if not isinstance(b, int):
        raise ValueError(f"B must be an integer, not {type(b)} ({b})")
    if not isinstance(atime, int):
        raise ValueError(f"atime must be an integer, not {type(atime)} ({atime})")
    if not isinstance(astep, int):
        raise ValueError(f"astep must be an integer, not {type(astep)} ({astep})")
    if not isinstance(gain, int) and gain != 0.5:
        if gain not in [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512]:
            raise ValueError(f"gain must be an integer, not {type(gain)} ({gain})")
    if r < 0 or r > 255:
        raise ValueError(f"R value {r} out of range (0..255)")
    if g < 0 or g > 255:
        raise ValueError(f"G value {g} out of range (0..255)")
    if b < 0 or b > 255:
        raise ValueError(f"B value {b} out of range (0..255)")
    if atime < 0 or atime > 255:
        raise ValueError(f"atime value {atime} out of range (0..255)")
    if astep < 0 or astep > 65535:
        raise ValueError(f"astep value {astep} out of range (0..65535)")
    if gain < 0.5 or gain > 512:
        raise ValueError(f"gain value {gain} out of range (0.5..512)")
    # END USER INPUT


def run_experiment(parameters, devices=None):
    if devices is None:
        devices = initialize_devices()

    # USER-DEFINED
    pixels = devices["pixels"]
    sensor = devices["sensor"]

    r, g, b = [parameters[key] for key in ["R", "G", "B"]]
    atime = parameters.get("atime", 100)
    astep = parameters.get("astep", 999)
    gain = parameters.get("gain", 128)

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


def reset_experiment(devices=None):
    if devices is None:
        devices = initialize_devices()

    # USER-DEFINED
    pixels = devices["pixels"]

    # Turn off the LED
    pixels[0] = (0, 0, 0)
    pixels.write()


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
        payload_data = {}
        # # pin numbers not used here, but can help with organization for complex tasks
        # p = int(t[5:])  # pin number

        print(msg)

        # careful not to throw an unrecoverable error due to bad request
        # Perform the experiment and record the results
        try:
            parameters = json.loads(msg)
            payload_data["_input_message"] = parameters

            # don't allow access to hardware if any input values are out of bounds
            validate_inputs(parameters)

            beep(buzzer)
            sensor_data = run_experiment(parameters, devices)
            payload_data = merge_two_dicts(payload_data, sensor_data)

        except Exception as err:
            print(err)
            if "_input_message" not in payload_data.keys():
                payload_data["_input_message"] = msg
            payload_data["error"] = get_traceback(err)

        try:
            payload_data["utc_timestamp"] = get_timestamp(timeout=2)
            payload_data["onboard_temperature_K"] = get_onboard_temperature(unit="K")
            payload_data["sd_card_ready"] = sdcard_ready
        except OverflowError as e:
            print(get_traceback(e))
        except Exception as e:
            print(get_traceback(e))

        # turn off the LEDs
        reset_experiment()
        payload = json.dumps(payload_data)
        print(payload)

        if sdcard_ready:
            try:
                write_payload_backup(payload, fpath=data_backup_fpath)
            except Exception as e:
                w = f"Failed to write to SD card: {get_traceback(e)}"
                print(w)
                payload_data["warning"] = w
                payload = json.dumps(payload_data)

        # prefer qos=1, but causes recursion error if too many messages in short period
        # of time
        client.publish(prefix + "as7341/", payload, qos=0)

        try:
            log_to_mongodb(
                payload_data,
                url=mongodb_url,
                api_key=mongodb_api_key,
                cluster_name=mongodb_cluster_name,
                database_name=mongodb_database_name,
                collection_name=mongodb_collection_name,
                verbose=True,
            )
        except Exception as e:
            print(f"Failed to log to MongoDB backend: {get_traceback(e)}")


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
client.on_connect = on_connect  # type: ignore
client.on_message = on_message  # type: ignore
client.subscribe(prefix + "GPIO/#")

heartbeat(True)
sign_of_life(True)

while True:
    client.check_msg()
    heartbeat(False)
    sign_of_life(False)


## Code Graveyard

# if sdcard_ready:
#     try:
#         write_payload_backup(payload, fpath=data_backup_fpath)
#     except Exception as e:
#         print(e)
#         print("failed to write payload backup to SD card")


# # Open the file we just created and read from it
# with open("/sd/test01.txt", "r") as file:
#     data = file.read()
#     print(data)
