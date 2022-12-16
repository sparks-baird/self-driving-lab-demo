import json

from self_driving_lab_demo.utils.observe import liquid_observe_sensor_data

with open("scripts/secrets.json", "r") as f:
    secrets = json.load(f)

sensor_data = liquid_observe_sensor_data(
    R=1.0,
    Y=0.0,
    B=0.0,
    prerinse_power=0.5,
    prerinse_time=10.0,
    runtime=4.0,
    pico_id=secrets["PICO_ID_3"],
)

print(sensor_data)

1 + 1
