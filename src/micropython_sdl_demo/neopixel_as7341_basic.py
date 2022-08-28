from time import sleep

import machine
import neopixel
from as7341_sensor import Sensor

num_pixels = 1
pin = machine.Pin(28)
pixels = neopixel.NeoPixel(pin, num_pixels)

pixels[0] = (100, 0, 0)

pixels.write()

sleep(0.5)

sensor = Sensor()
print(sensor.all_channels)

sleep(0.5)

pixels[0] = (0, 0, 0)

pixels.write()
