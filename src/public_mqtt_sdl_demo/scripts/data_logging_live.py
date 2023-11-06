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

from data_logging import log_to_mongodb
from netman import connectWiFi

connectWiFi(SSID, PASSWORD, country="US")

mongodb_url = f"https://data.mongodb-api.com/app/{MONGODB_APP_NAME}/endpoint/data/v1/action/insertOne"  # noqa: E501

t0 = time()
tf = 10

i = 0

while (time() - t0) < tf:
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

# ~2 seconds per datapoint (solely from MongoDB request)
