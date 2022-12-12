from secrets import (
    DEVICE_NICKNAME,
    MONGODB_API_KEY,
    MONGODB_COLLECTION_NAME,
    PASSWORD,
    SSID,
)

from data_logging import log_to_mongodb
from netman import connectWiFi

connectWiFi(SSID, PASSWORD, country="US")

mongodb_app_name = "data-sarkl"
mongodb_url = f"https://data.mongodb-api.com/app/{mongodb_app_name}/endpoint/data/v1/action/insertOne"  # noqa: E501
mongodb_cluster_name = "sparks-materials-informatics"
mongodb_database_name = "clslab-light-mixing"

log_to_mongodb(
    {"device_nickname": DEVICE_NICKNAME},
    api_key=MONGODB_API_KEY,
    collection_name=MONGODB_COLLECTION_NAME,
    url=mongodb_url,
    cluster_name=mongodb_cluster_name,
    database_name=mongodb_database_name,
    verbose=True,
    retries=2,
)
