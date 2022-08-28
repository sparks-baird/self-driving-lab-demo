from time import sleep

import machine
import neopixel

num_pixels = 1
pin = machine.Pin(28)
pixels = neopixel.NeoPixel(pin, num_pixels)

pixels[0] = (20, 0, 0)

pixels.write()

sleep(3)
pixels[0] = (0, 0, 0)

pixels.write()
