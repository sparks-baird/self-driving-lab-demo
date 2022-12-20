import json

from self_driving_lab_demo.utils.observe import (
    get_paho_client,
    mqtt_observe_sensor_data,
)

with open("scripts/secrets.json", "r") as f:
    secrets = json.load(f)

username = "sgbaird"
password = "D.Pq5gYtejYbU#L"
hostname = "248cc294c37642359297f75b7b023374.s2.eu.hivemq.cloud"
# pico_id = "test"
pico_id = secrets["SPARKS_LAB"]
prefix = f"sdl-demo/picow/{pico_id}/"
neopixel_topic = prefix + "GPIO/28"
port = 8883
sensor_topic = prefix + "as7341/"

client = get_paho_client(username, password, hostname, port, sensor_topic)

sensor_data = mqtt_observe_sensor_data(R=10, G=11, B=12, pico_id=pico_id, client=client)

1 + 1
