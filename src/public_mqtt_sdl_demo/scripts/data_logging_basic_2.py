# based on https://medium.com/@johnlpage/introduction-to-microcontrollers-and-the-pi-pico-w-f7a2d9ad1394
import urequests
from my_secrets import COURSE_ID, PASSWORD, SSID
from netman import connectWiFi

connectWiFi(SSID, PASSWORD, country="US")

API_KEY = "UT4cdinBetBaNqCBc5hISkaArhllv5dWfzXgbYsLYzpv79nqNhVwVsudQU5ZUmBE"  # Public API key for demo purposes only
CLUSTER_NAME = "test-cluster"
DATABASE_NAME = "test-db"
COLLECTION_NAME = "write-to-me"

URL_ENDPOINT = "https://us-east-2.aws.data.mongodb-api.com/app/data-ibmqs/endpoint/data/v1/action/insertOne"

headers = {"api-key": API_KEY}
document = {"course_id": COURSE_ID}

payload = {
    "dataSource": CLUSTER_NAME,
    "database": DATABASE_NAME,
    "collection": COLLECTION_NAME,
    "document": document,
}

print(f"sending document to {CLUSTER_NAME}:{DATABASE_NAME}:{COLLECTION_NAME}")

num_retries = 3
for _ in range(num_retries):
    response = urequests.post(URL_ENDPOINT, headers=headers, json=payload)
    txt = str(response.text)
    status_code = response.status_code

    print(f"Response: ({status_code}), msg = {txt}")

    response.close()

    if status_code == 201:
        print("Added Successfully")
        break

    print("Retrying...")
