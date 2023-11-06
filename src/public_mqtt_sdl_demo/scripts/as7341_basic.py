from as7341_sensor import Sensor

sensor = Sensor()

atime = 100
astep = 999
gain = 128

sensor._atime = atime
sensor._astep = astep
sensor._gain = gain

assert 0 <= atime <= 255, f"Invalid atime: {atime} (must be between 0 and 255)"
assert 0 <= astep <= 65536, f"Invalid astep: {astep} (must be between 0 and 65536)"
assert 0.5 <= gain <= 512, f"Invalid gain: {gain} (must be between 0.5 and 512)"

sensor_data = sensor.all_channels

CHANNEL_NAMES = [
    "ch410",
    "ch440",
    "ch470",
    "ch510",
    "ch550",
    "ch583",
    "ch620",
    "ch670",
]

sensor_data = {ch: datum for ch, datum in zip(CHANNEL_NAMES, sensor_data)}

print(sensor_data)
