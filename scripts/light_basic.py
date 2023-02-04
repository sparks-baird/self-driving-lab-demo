import json

from self_driving_lab_demo.utils.observe import (
    get_paho_client,
    mqtt_observe_sensor_data,
)

with open("scripts/secrets.json", "r") as f:
    secrets = json.load(f)

# pico_id = "test"
# pico_id = secrets["SPARKS_LAB"]
pico_id = secrets["SPARKS_1"]
sensor_topic = f"sdl-demo/picow/{pico_id}/as7341/"

client = get_paho_client(sensor_topic)

sensor_data = mqtt_observe_sensor_data(
    R=10, G=11, B=12, pico_id=pico_id, client=client, mongodb=True
)

1 + 1
