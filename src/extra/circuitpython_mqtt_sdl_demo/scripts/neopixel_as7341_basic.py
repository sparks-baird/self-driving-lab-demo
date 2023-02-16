from secrets import PASSWORD, SSID

import adafruit_requests
import board
import busio
import neopixel
import socketpool
import wifi
from adafruit_as7341 import AS7341

TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, None)

wifi.radio.connect(SSID, PASSWORD)

with requests.get(TEXT_URL) as r:
    print(f"{r.status_code} {r.reason.decode()} {r.content}")

pixel_pin = board.GP28
num_pixels = 1

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.35, auto_write=False)

i2c = busio.I2C(sda=board.GP26, scl=board.GP27)  # see Maker Pi Pico Base pinout

# i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = AS7341(i2c)

pixels.fill((100, 100, 100))
pixels.show()

print(sensor.all_channels)

pixels.fill((0, 0, 0))
pixels.show()
