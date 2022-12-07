import json

from self_driving_lab_demo.utils.observe import liquid_observe_sensor_data

with open("scripts/secrets.json", "r") as f:
    secrets = json.load(f)

liquid_observe_sensor_data(
    0.25,
    0.25,
    0.25,
    water=0.25,
    prerinse_time=2.0,
    runtime=2.0,
    pico_id=secrets["PICO_ID_3"],
)

1 + 1
