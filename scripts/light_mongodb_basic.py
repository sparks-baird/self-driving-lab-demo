import json

import pymongo

# from self_driving_lab_demo.utils.data_logging import log_to_mongodb
from self_driving_lab_demo.utils.observe import (
    get_paho_client,
    mqtt_observe_sensor_data,
)

database_name = "clslab-light-mixing"
collection_name = "developer"

with open("scripts/secrets.json", "r") as f:
    secrets = json.load(f)

pico_id = "test"
# pico_id = secrets["SPARKS_LAB"]
sensor_topic = f"sdl-demo/picow/{pico_id}/as7341/"

client = get_paho_client(sensor_topic)

sensor_data = mqtt_observe_sensor_data(
    R=10, G=11, B=12, pico_id=pico_id, client=client, mongodb=True
)

# MONGODB_APP_NAME = secrets["MONGODB_APP_NAME"]
# url =
# f"https://data.mongodb-api.com/app/{MONGODB_APP_NAME}/endpoint/data/v1/action/insertOne" # noqa: E501

username = secrets["PYMONGO_USERNAME"]
password = secrets["PYMONGO_PASSWORD"]
client = pymongo.MongoClient(
    f"mongodb+srv://{username}:{password}@sparks-materials-inform.bgydt.mongodb.net/?retryWrites=true&w=majority"  # noqa: E501
)
db = client[database_name]
collection = db[collection_name]
id = collection.insert_one(sensor_data).inserted_id


# log_to_mongodb(
#     sensor_data,
#     url,
#     secrets["MONGODB_API_KEY"],
#     secrets["MONGODB_CLUSTER_NAME"],
#     secrets["MONGODB_DATABASE_NAME"],
#     secrets["MONGODB_COLLECTION_NAME"],
# )


1 + 1
