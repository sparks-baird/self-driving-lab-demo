"""
https://gist.github.com/sammachin/b67cc4f395265bccd9b2da5972663e6d
http://www.steves-internet-guide.com/into-mqtt-python-client/
"""

import json
import sys
from secrets import PASSWORD, SSID
from time import sleep, ticks_diff, ticks_ms

import network
from as7341_sensor import Sensor
from machine import PWM, Pin, unique_id
from neopixel import NeoPixel
from ubinascii import hexlify
from uio import StringIO
from umqtt.simple import MQTTClient

my_id = hexlify(unique_id()).decode()

prefix = f"sdl-demo/picow/{my_id}/"

print(f"prefix: {prefix}")

pixels = NeoPixel(Pin(28), 1)  # one NeoPixel on Pin 28 (GP28)
sensor = Sensor()

try:
    onboard_led = Pin("LED", Pin.OUT)  # only works for Pico W
except Exception as e:
    print(e)
    onboard_led = Pin(25, Pin.OUT)

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


def beep(power=0.005):
    buzzer.freq(300)
    buzzer.duty_u16(round(65535 * power))
    sleep(0.15)
    buzzer.duty_u16(0)


def get_traceback(err):
    try:
        with StringIO() as f:
            sys.print_exception(err, f)
            return f.getvalue()
    except Exception as err2:
        print(err2)
        return f"Failed to extract file and line number due to {err2}.\nOriginal error: {err}"  # noqa: E501


def validate_inputs(r, g, b, atime, astep, gain):
    # don't allow access to hardware if any input values are out of bounds
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


def reset_experiment():
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
        sensor_data_dict = {}
        # # pin numbers not used here, but can help with organization for complex tasks
        # p = int(t[5:])  # pin number

        print(msg)

        # careful not to throw an unrecoverable error due to bad request
        # Perform the experiment and record the results
        try:
            data = json.loads(msg)
            sensor_data_dict["_input_message"] = data
            r, g, b = [data[key] for key in ["R", "G", "B"]]
            atime = data.get("atime", 100)
            astep = data.get("astep", 999)
            gain = data.get("gain", 128)

            # don't allow access to hardware if any input values are out of bounds
            validate_inputs(r, g, b, atime, astep, gain)

            beep()  # REVIEW: where to put the beep?
            pixels[0] = (r, g, b)
            pixels.write()

            sensor._atime = atime
            sensor._astep = astep
            sensor._gain = gain
            sensor_data = sensor.all_channels

            for ch, datum in zip(CHANNEL_NAMES, sensor_data):
                sensor_data_dict[ch] = datum
        except Exception as err:
            print(err)
            if "_input_message" not in sensor_data_dict.keys():
                sensor_data_dict["_input_message"] = msg
            sensor_data_dict["error"] = get_traceback(err)

        # turn off the LEDs
        reset_experiment()
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
client.on_connect = on_connect
client.on_message = on_message
client.subscribe(prefix + "GPIO/#")

heartbeat(True)
sign_of_life(True)

while True:
    client.check_msg()
    heartbeat(False)
    sign_of_life(False)


# %% Code Graveyard
#  with open(f"{log_dir}/error-{i}.txt", "w") as f:
#      sys.print_exception(e, f)
#  with open(f"{log_dir}/error-{i}.txt", "r") as f:
#      e = f.readlines()
#      e = " ".join(e)
#  sensor_data_dict["error"] = e

# import errno
# import os
# log_dir = "logs"
# try:
#     os.mkdir(log_dir)
# except OSError as exc:
#     if exc.errno != errno.EEXIST:
#         raise
#     pass

# try:
#     data = json.loads(msg)
#     sensor_data_dict["_input_message"] = data
# except (json.JSONDecodeError, TypeError) as json_err:
#     try:
#         with StringIO() as f:
#             sys.print_exception(json_err, f)
#             sensor_data_dict["error"] = f.getvalue()
#     except Exception as err2:
#         print(err2)
#         sensor_data_dict[
#             "error"
#         ] = f"Failed to extract file and line number due to {err2}.\nOriginal error: {err}"
#     sensor_data_dict[
#         "_input_message"
#     ] = f"json.loads({msg}) failed. {json_err}"

# sensor_data_dict["_session_id"] = sensor_data_dict.get("_session_id", None)

# sensor_data_dict["_experiment_id"] = sensor_data_dict.get(
#     "_experiment_id", None
# )

# try:
#     p = int(t[5:])  # pin number
#     sensor_data_dict["pin"] = p
# except Exception as e:
#     print(e)
#     sensor_data_dict["pin"] = e
