import json

from self_driving_lab_demo.utils.observe import (
    get_paho_client,
    liquid_observe_sensor_data,
)

with open("scripts/secrets.json", "r") as f:
    secrets = json.load(f)

pico_id = secrets["PICO_ID_3"]
sensor_topic = f"sdl-demo/picow/{pico_id}/as7341/"

client = get_paho_client(sensor_topic)

sensor_data = liquid_observe_sensor_data(
    R=0.5,
    Y=0.5,
    B=0.5,
    prerinse_power=0.75,
    prerinse_time=10.0,
    runtime=10.0,
    pico_id=pico_id,
    client=client,
)

print(sensor_data)

1 + 1
