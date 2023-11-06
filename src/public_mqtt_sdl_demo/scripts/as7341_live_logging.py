from secrets import (
    MONGODB_API_KEY,
    MONGODB_APP_NAME,
    MONGODB_CLUSTER_NAME,
    MONGODB_COLLECTION_NAME,
    MONGODB_DATABASE_NAME,
    PASSWORD,
    SSID,
)
from time import time

from as7341_sensor import Sensor
from data_logging import log_to_mongodb
from netman import connectWiFi

connectWiFi(SSID, PASSWORD, country="US")

sensor = Sensor()

# atime = 100
# astep = 999
atime = 1
astep = 1
gain = 128


mongodb_url = f"https://data.mongodb-api.com/app/{MONGODB_APP_NAME}/endpoint/data/v1/action/insertOne"  # noqa: E501

sensor._atime = atime
sensor._astep = astep
sensor._gain = gain

assert 0 <= atime <= 255, f"Invalid atime: {atime} (must be between 0 and 255)"
assert 0 <= astep <= 65536, f"Invalid astep: {astep} (must be between 0 and 65536)"
assert 0.5 <= gain <= 512, f"Invalid gain: {gain} (must be between 0.5 and 512)"

t0 = time()
tf = 10

i = 0

while (time() - t0) < tf:
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

    sensor_data = {
        "ch583": 0,
        "ch670": 0,
        "ch510": 0,
        "ch410": 0,
        "ch620": 0,
        "ch470": 0,
        "ch550": 0,
        "ch440": 0,
    }
    log_to_mongodb(
        sensor_data,
        url=mongodb_url,
        api_key=MONGODB_API_KEY,
        cluster_name=MONGODB_CLUSTER_NAME,
        database_name=MONGODB_DATABASE_NAME,
        collection_name=MONGODB_COLLECTION_NAME,
        verbose=True,
        retries=2,
    )

    i = i + 1

print(f"Number datapoints within {tf} seconds: {i}")
