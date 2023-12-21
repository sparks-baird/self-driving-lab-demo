import asyncio

from mqtt_as import MQTTClient, config

# Local configuration
config["ssid"] = "your_network_name"  # Optional on ESP8266
config["wifi_pw"] = "your_password"
config["server"] = "192.168.0.10"  # Change to suit e.g. 'iot.eclipse.org'


async def messages(client):  # Respond to incoming messages
    async for topic, msg, retained in client.queue:
        print((topic, msg, retained))


async def up(client):  # Respond to connectivity being (re)established
    while True:
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe("foo_topic", 1)  # renew subscriptions


async def main(client):
    await client.connect()
    for coroutine in (up, messages):
        asyncio.create_task(coroutine(client))
    n = 0
    while True:
        await asyncio.sleep(5)
        print("publish", n)
        # If WiFi is down the following will pause for the duration.
        await client.publish("result", "{}".format(n), qos=1)
        n += 1


config["queue_len"] = 1  # Use event interface with default queue size
MQTTClient.DEBUG = True  # Optional: print diagnostic messages
client = MQTTClient(config)
try:
    asyncio.run(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
