from time import sleep

from machine import Pin
from neopixel import NeoPixel

pixels = NeoPixel(Pin(28), 1)  # 1 pixel on Pin 28

pixels[0] = (50, 50, 50)
pixels.write()

sleep(2.0)

pixels[0] = (0, 0, 0)
pixels.write()
