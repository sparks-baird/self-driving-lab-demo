from public_mqtt_sdl_demo.secrets import PICO_ID
from self_driving_lab_demo.utils.observe import mqtt_observe_sensor_data

for x in range(10, 101, 5):
    mqtt_observe_sensor_data(x, x, x, pico_id=PICO_ID)

1 + 1
