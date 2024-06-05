import json
import ssl
from secrets import (
    HIVEMQ_HOST,
    HIVEMQ_PASSWORD,
    HIVEMQ_USERNAME,
    MONGODB_API_KEY,
    MONGODB_COLLECTION_NAME,
    PASSWORD,
    SSID,
)

# from as7341_sensor import Sensor
from time import sleep

import ntptime
from data_logging import get_traceback, log_to_mongodb
from netman import connectWiFi
from sdl_demo_utils import get_onboard_led, heartbeat, sign_of_life
from umqtt.simple2 import MQTTClient

connectWiFi(SSID, PASSWORD, country="US")

onboard_led = get_onboard_led()

# To validate certificates, a valid time is required
ntptime.timeout = 5  # type: ignore
ntptime.host = "de.pool.ntp.org"
ntptime.settime()

print("Obtaining CA Certificate")
with open("hivemq-com-chain.der", "rb") as f:
    cacert = f.read()
f.close()

my_id = "test"
prefix = f"sdl-demo/picow/{my_id}/"
port = 8883

mongodb_app_name = "data-sarkl"
mongodb_url = f"https://data.mongodb-api.com/app/{mongodb_app_name}/endpoint/data/v1/action/insertOne"  # noqa: E501
mongodb_cluster_name = "sparks-materials-informatics"
mongodb_database_name = "clslab-light-mixing"


def callback(topic, msg, retain=None, dup=None):
    parameters = json.loads(msg)

    # payload_data = run_experiment(parameters)

    payload_data = {
        "device_nickname": "CLSLab-light-public-test",
        "_input_msg": {
            "_session_id": "97385e3c-f341-4c37-a64f-6c80b92192bd",
            "B": 12,
            "atime": 100,
            "gain": 128.0,
            "integration_time_s": 0.28078,
            "astep": 999,
            "G": 11,
            "R": 10,
            "_experiment_id": "0ff224fe-7be8-4315-940c-950369dec29f",
        },
    }
    payload = json.dumps(payload_data)
    print(payload)
    client.publish(prefix + "as7341/", payload, qos=0)

    log_to_mongodb(
        payload_data,
        api_key=MONGODB_API_KEY,
        collection_name=MONGODB_COLLECTION_NAME,
        url=mongodb_url,
        cluster_name=mongodb_cluster_name,
        database_name=mongodb_database_name,
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
        "cert_reqs": ssl.CERT_REQUIRED,
        "cadata": cacert,
        "server_hostname": HIVEMQ_HOST,
    },
)
try:
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
        client.check_msg()
        heartbeat(client, False)
        sign_of_life(onboard_led, False)
except Exception as e:
    client.disconnect()
    raise e
