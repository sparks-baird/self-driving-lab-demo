# Write your code here :-)
import asyncio
import time

import adafruit_requests
import board
import digitalio
import socketpool
import wifi
from adafruit_httpserver import HTTPResponse, HTTPServer

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Wifi Stuff
TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)
requests = adafruit_requests.Session(pool, None)

try:
    wifi.radio.connect(secrets["ssid"], secrets["password"])
except Exception as e:
    print(f"Error: {e}")

# LED Stuff
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


@server.route("/")
def base(request):
    return HTTPResponse(filename="/index.html")


def blink_led():
    counter = 0
    while True:
        if counter % 3 == 0:
            print(f"\nWe are running! ({counter/3})")
            print(f"My IP:\t{wifi.radio.ipv4_address}")
        led.value = not led.value
        time.sleep(5)
        counter += 1


try:
    server.start(str(wifi.radio.ipv4_address), root="/")
except OSError as e:
    print(f"\nError: {e}")

asyncio.run(blink_led())

while True:
    try:
        server.poll()
    except OSError as e:
        print(f"\nError: {e}")
