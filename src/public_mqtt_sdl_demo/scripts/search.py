"""https://www.steves-internet-guide.com/receiving-messages-mqtt-python-clientq=Queue()"""
import json
from queue import Queue
from secrets import PICO_ID

import paho.mqtt.client as mqtt

sensor_data_queue: Queue[dict] = Queue()
timeout = 30


def on_message(client, userdata, msg):
    sensor_data_queue.put(json.loads(msg.payload))


def observe_sensor_data(R, G, B, pico_id=PICO_ID, hostname="test.mosquitto.org"):

    prefix = f"sdl-demo/picow/{pico_id}/"
    neopixel_topic = prefix + "GPIO/28"
    sensor_topic = prefix + "as7341/"

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(sensor_topic)

    client = mqtt.Client()  # create new instance
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(hostname)  # connect to broker
    client.subscribe(sensor_topic)

    # ensures double quotes for JSON compatiblity
    payload = json.dumps(dict(R=R, G=G, B=B))
    client.publish(neopixel_topic, payload)

    # t = time()
    while sensor_data_queue.empty():
        client.loop()
    return sensor_data_queue.get()


sensor_data = observe_sensor_data(5, 10, 15, pico_id=PICO_ID)
print(sensor_data)
sensor_data = observe_sensor_data(50, 60, 40, pico_id=PICO_ID)
print(sensor_data)
sensor_data = observe_sensor_data(0, 0, 0, pico_id=PICO_ID)
print(sensor_data)


# import paho.mqtt.subscribe as subscribe
# import paho.mqtt.publish as publish
# publish.single(prefix + "GPIO/28", payload, hostname=hostname)
# msg = subscribe.simple(prefix + "as7341", hostname=hostname)
# sensor_data = json.loads(msg.payload)["sensor_data"]
# print(sensor_data)
