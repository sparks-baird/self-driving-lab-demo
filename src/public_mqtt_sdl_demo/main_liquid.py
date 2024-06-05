"""Run a materials acceleration platform demo on a Raspberry Pi Pico W."""

import gc
import json
import os
import ssl
from secrets import HIVEMQ_HOST, HIVEMQ_PASSWORD, HIVEMQ_USERNAME, PASSWORD, SSID
from time import sleep

import ntptime
from as7341_sensor import Sensor
from data_logging import initialize_sdcard, log_to_mongodb
from machine import PWM, Pin, reset, unique_id
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

##### BEGIN USER-DEFINED IMPORTS #####
from time import ticks_diff, ticks_ms

##### END USER-DEFINED IMPORTS #####

# sleep to avoid KeyboardInterrupt overwriting log.txt when opening in Thonny
sleep(5.0)

try:
    gc.collect()
    port = 8883

    logfile = open("log.txt", "w")
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
    ntptime.timeout = 10  # type: ignore
    ntptime.host = "de.pool.ntp.org"
    try:
        ntptime.settime()
    except Exception as e:
        ntptime.settime()

    print("Obtaining CA Certificate")
    with open("hivemq-com-chain.der", "rb") as f:
        cacert = f.read()
    f.close()

    logfile.close()
    os.dupterm(None)

    ######################################
    #### BEGIN USER-DEFINED FUNCTIONS ####
    ######################################

    PUMP_PINS = {"R": 0, "Y": 1, "B": 2, "water": 3}
    pumps = {name: PWM(Pin(i)) for name, i in PUMP_PINS.items()}
    white_led = Pin(9, mode=Pin.OUT)
    sensor = Sensor()

    white_led.on()

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
        prerinse_power = parameters.get("prerinse_power", 1.0)
        prerinse_time = parameters.get("prerinse_time", 10.0)
        run_pump(water_pump, prerinse_power)
        sleep(prerinse_time)

        runtime = parameters.get("runtime", 10.0)
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
        if devices is None:
            devices = get_devices()

        pumps = devices["pumps"]
        water_pump = pumps["water"]
        # white_led = devices["white_led"]
        sensor = devices["sensor"]

        # white_led.on()

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

        sleep(1.0)
        prerinse_background_data = sensor.all_channels
        prerinse_background_data = {
            ch: datum for ch, datum in zip(CHANNEL_NAMES, prerinse_background_data)
        }

        atime = parameters.get("atime", 100)
        astep = parameters.get("astep", 999)
        gain = parameters.get("gain", 128)

        sensor._atime = atime
        sensor._astep = astep
        sensor._gain = gain

        # REVIEW: probably better to rinse at beginning of experiment than end
        prerinse_power = parameters.get("prerinse_power", 1.0)
        prerinse_time = parameters.get("prerinse_time", 10.0)
        run_pump(water_pump, prerinse_power)
        sleep(prerinse_time)

        sleep(1.0)
        background_data = sensor.all_channels
        background_data = {
            ch: datum for ch, datum in zip(CHANNEL_NAMES, background_data)
        }

        runtime = parameters.get("runtime", 10.0)
        keys = list(pumps.keys())
        run_pumps(
            [pumps[key] for key in keys],
            [parameters[key] for key in keys],
            runtime,
        )

        sleep(1.0)
        sensor_data = sensor.all_channels
        # white_led.off()
        sensor_data = {ch: datum for ch, datum in zip(CHANNEL_NAMES, sensor_data)}
        sensor_data["prerinse_background"] = prerinse_background_data
        sensor_data["background"] = background_data
        return sensor_data

    def reset_experiment(parameters, devices=None):
        if devices is None:
            devices = get_devices()

        pumps = devices["pumps"]
        # white_led = devices["white_led"]

        # white_led.off()

        # Turn off the pumps
        [run_pump(pump, 0.0) for pump in pumps.values()]

    def emergency_shutdown(devices=None):
        # in CLSLabs:Liquid case, same as reset_experiment
        if devices is None:
            devices = get_devices()

        pumps = devices["pumps"]
        # white_led = devices["white_led"]

        # white_led.off()

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

            if experiment.sdcard_ready:
                payload_data = experiment.write_to_sd_card(
                    payload_data, fpath=sdcard_backup_fpath
                )

            # prefer qos=1, but causes recursion error if too many messages in short period
            # of time
            payload_data["device_nickname"] = DEVICE_NICKNAME
            payload_data["encrypted_device_id_truncated"] = trunc_device_id
            try:
                parameters = json.loads(msg)
                if parameters.get("mongodb", True):
                    log_to_mongodb(
                        payload_data,
                        url=mongodb_url,
                        api_key=MONGODB_API_KEY,
                        cluster_name=MONGODB_CLUSTER_NAME,
                        database_name=MONGODB_DATABASE_NAME,
                        collection_name=MONGODB_COLLECTION_NAME,
                        verbose=True,
                        retries=2,
                    )
                    payload_data["logged_to_mongodb"] = True
                else:
                    payload_data["logged_to_mongodb"] = False
            except Exception as e:
                payload_data["logged_to_mongodb"] = False
                print(get_traceback(e))

            payload = json.dumps(payload_data)
            print(payload)

            client.publish(prefix + "as7341/", payload, qos=0)

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
            "cert_reqs": ssl.CERT_REQUIRED,
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
            print(get_traceback(e))
            print("Reconnecting to WiFi...")
            connectWiFi(SSID, PASSWORD, country="US")
            client.connect(clean_session=False)
            client.set_callback(callback)
            client.subscribe(prefix + "GPIO/#")
except Exception as e:
    fname = "error.txt"
    logfile = open(fname, "w")
    logfile.write(get_traceback(e))
    logfile.close()
    reset()

# %% Code Graveyard

# control_inputs(parameters, devices=devices)
# sensor_data = measure_sensors(parameters, devices=devices)
