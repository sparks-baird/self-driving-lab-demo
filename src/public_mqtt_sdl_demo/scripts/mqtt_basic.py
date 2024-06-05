import json
import ssl
from secrets import (
    DEVICE_NICKNAME,
    HIVEMQ_HOST,
    HIVEMQ_PASSWORD,
    HIVEMQ_USERNAME,
    PASSWORD,
    SSID,
)
from time import sleep

import ntptime
from data_logging import get_traceback
from netman import connectWiFi
from sdl_demo_utils import get_onboard_led, heartbeat, sign_of_life
from umqtt.simple2 import MQTTClient

connectWiFi(SSID, PASSWORD, country="US")

onboard_led = get_onboard_led()

# To validate certificates, a valid time is required
ntptime.host = "de.pool.ntp.org"
ntptime.settime()

print("Obtaining CA Certificate")
with open("hivemq-com-chain.der", "rb") as f:
    cacert = f.read()
f.close()

my_id = "test"
prefix = f"sdl-demo/picow/{my_id}/"
port = 8883


def callback(topic, msg, retain=None, dup=None):
    parameters = json.loads(msg)

    # write code to run experiment, get payload_data

    payload_data = {"device_nickname": DEVICE_NICKNAME, "_input_msg": parameters}
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
