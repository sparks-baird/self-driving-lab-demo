"""
https://gist.github.com/sammachin/b67cc4f395265bccd9b2da5972663e6d
http://www.steves-internet-guide.com/into-mqtt-python-client/
"""

import json
import time
from secrets import PASSWORD, SSID

try:
    from secrets import MONGODB_API_KEY
except Exception as e:
    print(e)

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
from sdl_demo_utils import beep, get_traceback, merge_two_dicts
from ubinascii import hexlify
from ufastrsa.genprime import genrsa
from ufastrsa.rsa import RSA
from umqtt.simple import MQTTClient

my_id = hexlify(unique_id()).decode()

bits = 256
cipher = RSA(*genrsa(bits, e=65537))

prefix = f"sdl-demo/picow/{my_id}/"

print(f"prefix: {prefix}")

# https://medium.com/@johnlpage/introduction-to-microcontrollers-and-the-pi-pico-w-f7a2d9ad1394
# for a tutorial on how to use MongoDB Atlas with the Pico W, but you're welcome and
# encouraged to log to the public MongoDB instance via the information below :)
mongodb_app_name = "data-sarkl"
mongodb_url = f"https://data.mongodb-api.com/app/{mongodb_app_name}/endpoint/data/v1/action/insertOne"  # noqa: E501
mongodb_cluster_name = "sparks-materials-informatics"
mongodb_database_name = "clslab-liquid-mixing"
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
    PUMP_PINS = {"red": 0, "yellow": 1, "blue": 2, "water": 3}
    pumps = {name: PWM(Pin(i)) for name, i in PUMP_PINS.items()}
    sensor = Sensor()
    return {"pumps": pumps, "sensor": sensor}


devices = initialize_devices()


def validate_inputs(parameters, devices=None):
    # don't allow access to hardware if any input values are out of bounds

    # USER-DEFINED
    r, y, b, w = [parameters[key] for key in ["R", "Y", "B", "water"]]
    runtime = parameters.get("runtime", 5)
    prerinse_time = parameters.get("prerinse_time", 5)

    atime = parameters.get("atime", 100)
    astep = parameters.get("astep", 999)
    gain = parameters.get("gain", 128)

    if not isinstance(r, float):
        raise ValueError(f"R must be a float, not {type(r)} ({r})")

    if not isinstance(y, float):
        raise ValueError(f"Y must be a float, not {type(y)} ({y})")

    if not isinstance(b, float):
        raise ValueError(f"B must be a float, not {type(b)} ({b})")

    if not isinstance(w, float):
        raise ValueError(f"water must be a float, not {type(w)} ({w})")

    if not isinstance(atime, int):
        raise ValueError(f"atime must be an integer, not {type(atime)} ({atime})")

    if not isinstance(astep, int):
        raise ValueError(f"astep must be an integer, not {type(astep)} ({astep})")

    if not isinstance(gain, int) and gain != 0.5:
        if gain not in [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512]:
            raise ValueError(f"gain must be an integer, not {type(gain)} ({gain})")

    if not isinstance(runtime, float):
        raise ValueError(f"runtime must be a float, not {type(runtime)} ({runtime})")

    if not isinstance(prerinse_time, float):
        raise ValueError(
            f"prerinse_time must be a float, not {type(prerinse_time)} ({prerinse_time})"
        )

    if r < 0 or r > 1:
        raise ValueError(f"R value {r} out of range (0..1)")

    if y < 0 or y > 1:
        raise ValueError(f"G value {y} out of range (0..1)")

    if b < 0 or b > 1:
        raise ValueError(f"B value {b} out of range (0..1)")

    if w < 0 or w > 1:
        raise ValueError(f"water value {w} out of range (0..1)")

    if atime < 0 or atime > 255:
        raise ValueError(f"atime value {atime} out of range (0..255)")

    if astep < 0 or astep > 65535:
        raise ValueError(f"astep value {astep} out of range (0..65535)")

    if gain < 0.5 or gain > 512:
        raise ValueError(f"gain value {gain} out of range (0.5..512)")

    if runtime < 1 or runtime > 100:
        raise ValueError(f"runtime value {runtime} out of range (1..100)")

    if prerinse_time < 1 or prerinse_time > 100:
        raise ValueError(f"prerinse_time value {prerinse_time} out of range (1..100)")
    # END USER INPUT


def run_pump(pump, power):
    pump.freq(20000)
    pump.duty_u16(round(65535 * power))


def run_pumps(pumps, powers, runtime):
    runtime_ms = runtime * 1000
    t0 = time.ticks_ms()

    for pump, power in zip(pumps, powers):
        pump.freq(20000)
        pump.duty_u16(round(65535 * power))

    while True:
        if time.ticks_diff(time.ticks_ms(), t0) > runtime_ms:
            break
        sleep(0.01)


def control_inputs(parameters, devices=None):
    if devices is None:
        devices = initialize_devices()

    # USER-DEFINED
    pumps = devices["pumps"]
    water_pump = pumps["water"]

    # REVIEW: probably better to rinse at beginning of experiment than end
    run_pump(water_pump, 1.0)
    rinse_time = parameters.get("prerinse_time", 5)
    sleep(rinse_time)

    keys = list(pumps.keys())

    run_pumps(
        [pumps[key] for key in keys],
        [parameters[key] for key in keys],
        parameters["runtime"],
    )


def measure_sensors(parameters, devices=None):
    if devices is None:
        devices = initialize_devices()

    sensor = devices["sensor"]

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
        devices = initialize_devices()

    pumps = devices["pumps"]

    # Turn off the pumps
    [run_pump(pump, 0.0) for pump in pumps]


def emergency_shutdown(devices=None):
    # in CLSLabs:Liquid case, same as reset_experiment
    if devices is None:
        devices = initialize_devices()

    pumps = devices["pumps"]

    # Turn off the pumps
    [run_pump(pump, 0.0) for pump in pumps]


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
            sensor_data = run_experiment(parameters, devices=devices)
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

        try:
            parameters = json.loads(msg)
            reset_experiment(parameters, devices=devices)
        except Exception as e:
            emergency_shutdown(devices=devices)
            payload_data["reset_error"] = get_traceback(e)

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
                api_key=MONGODB_API_KEY,
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

print("Waiting for experiment requests...")

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
