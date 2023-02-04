"""
https://gist.github.com/sammachin/b67cc4f395265bccd9b2da5972663e6d
http://www.steves-internet-guide.com/into-mqtt-python-client/
"""

import json
from secrets import PASSWORD, SSID

try:
    from secrets import DEVICE_NICKNAME, MONGODB_API_KEY, MONGODB_COLLECTION_NAME
except Exception as e:
    print(e)

from time import sleep

from data_logging import initialize_sdcard
from machine import PWM, Pin, unique_id
from netman import connectWiFi
from sdl_demo_utils import (
    DummyMotor,
    DummySensor,
    Experiment,
    encrypt_id,
    get_onboard_led,
    get_traceback,
    heartbeat,
    sign_of_life,
)
from ubinascii import hexlify
from umqtt.simple import MQTTClient

# https://medium.com/@johnlpage/introduction-to-microcontrollers-and-the-pi-pico-w-f7a2d9ad1394
# you can request a MongoDB collection specific to you by emailing
# sterling.baird@utah.edu
mongodb_app_name = "data-sarkl"
mongodb_url = f"https://data.mongodb-api.com/app/{mongodb_app_name}/endpoint/data/v1/action/insertOne"  # noqa: E501
mongodb_cluster_name = "sparks-materials-informatics"
mongodb_database_name = "clslab-light-mixing"

connectWiFi(SSID, PASSWORD, country="US")

my_id = hexlify(unique_id()).decode()
my_encrypted_id = encrypt_id(my_id, verbose=True)
trunc_device_id = str(my_encrypted_id)[0:10]
prefix = f"sdl-demo/picow/{my_id}/"
mqtt_host = "test.mosquitto.org"

print(f"Unencrypted PICO ID (keep private): {my_id}")
print(f"Encrypted PICO ID (OK to share publicly): {my_encrypted_id}")
print(f"Truncated, encrypted PICO ID (OK to share publicly): {trunc_device_id}")
print(f"MQTT prefix: {prefix}")

sdcard_backup_fpath = "/sd/experiments.txt"

######################################
#### BEGIN USER-DEFINED FUNCTIONS ####
######################################

# at minimum, the following functions should be defined:
# - run_experiment (use a parameters dict to run experiment and return sensor data)
# - initialize_devices (return dict mapping from device name to device object)
# - reset_experiment (reset experiment to initial state)
# - emergency_shutdown (can be same as reset_experiment if needed)
# - validate_inputs (check that input parameters are valid)

# device objects should be defined here
motor = DummyMotor()
motor2 = DummyMotor()
sensor = DummySensor()

motor_name_1 = "motor1"
motor_name_2 = "motor2"
sensor_name = "sensor"


def get_devices() -> dict:
    # enforce instantiation of the devices a single time (i.e. singleton function)
    # if irrelevant, this function can return an empty dict: {}
    return {motor_name_1: motor, sensor_name: sensor, motor_name_2: motor2}


def validate_inputs(parameters, devices=None):
    # don't allow access to hardware if any input values are out of bounds
    # check input parameters. If invalid, raise an error
    # For example:
    # if parameters["temperature_K"] > 1000:
    #     raise ValueError("Temperature too high!")
    pass


def run_experiment(parameters, devices=None):
    if devices is None:
        devices = get_devices()

    motor1 = devices[motor_name_1]
    motor2 = devices[motor_name_2]
    sensor = devices[sensor_name]

    # enter code that will run the experiment and return sensor data

    # dummy sensor data
    sensor_data = {"sensor_output_A": 1.0, "sensor_output_B": 2.5}
    return sensor_data


def reset_experiment(parameters, devices=None):
    # for example, turn off the motors, home a stage, etc.
    # sometimes it might make sense to perform the resetting of the experiment during
    # the run_experiment function: for example, when rinsing out a chamber, since the
    # rinse time and power might be one of the input parameters that gets tracked
    pass


def emergency_shutdown(devices=None):
    # if reset_experiment causes an error, then this function will be called
    # for example, shut off the main power
    # this function can be the same as reset_experiment if needed
    pass


######################################
##### END USER-DEFINED FUNCTIONS #####
######################################

devices = get_devices()

onboard_led = get_onboard_led()
buzzer = PWM(Pin(18))
sdcard_ready = initialize_sdcard()


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
        experiment = Experiment(
            validate_inputs_fn=validate_inputs,
            run_experiment_fn=run_experiment,
            reset_experiment_fn=reset_experiment,
            emergency_shutdown_fn=reset_experiment,
            devices=devices,
            buzzer=buzzer,
        )
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
        )


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


client = MQTTClient(
    prefix,
    mqtt_host,
    user=None,
    password=None,
    keepalive=30,
    ssl=False,
    ssl_params={},
)
try:
    client.connect()
except OSError as e:
    print(get_traceback(e))
    print("Retrying client.connect() in 2 seconds...")
    sleep(2.0)
    client.connect()

client.set_callback(callback)
client.on_connect = on_connect  # type: ignore
client.on_message = on_message  # type: ignore
client.subscribe(prefix + "GPIO/#")

heartbeat(client, True)
sign_of_life(onboard_led, True)

print("Waiting for experiment requests...")

while True:
    client.check_msg()
    heartbeat(client, False)
    sign_of_life(onboard_led, False)


## Code Graveyard
