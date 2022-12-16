import json

from self_driving_lab_demo.utils.observe import (
    get_paho_client,
    mqtt_observe_sensor_data,
)

username = "sgbaird"
password = "D.Pq5gYtejYbU#L"
hostname = "248cc294c37642359297f75b7b023374.s2.eu.hivemq.cloud"
pico_id = "test"
prefix = f"sdl-demo/picow/{pico_id}/"
neopixel_topic = prefix + "GPIO/28"
port = 8883
sensor_topic = prefix + "as7341/"

client = get_paho_client(username, password, hostname, port, sensor_topic)

with open("scripts/secrets.json", "r") as f:
    secrets = json.load(f)

# mqtt_observe_sensor_data(R=10, G=11, B=12, pico_id=secrets["PICO_ID_1"])
mqtt_observe_sensor_data(R=10, G=11, B=12, pico_id="test", client=client)

1 + 1
