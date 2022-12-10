import json

from self_driving_lab_demo.utils.observe import mqtt_observe_sensor_data

with open("scripts/secrets.json", "r") as f:
    secrets = json.load(f)

mqtt_observe_sensor_data(R=10, G=11, B=12, pico_id=secrets["PICO_ID_1"])
mqtt_observe_sensor_data(R=10, G=11, B=12, pico_id="test")

1 + 1
