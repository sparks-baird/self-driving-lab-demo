"""Light the LED, then print the recorded channel measurements.

https://learn.pimoroni.com/article/getting-started-with-blinkt
https://github.com/adafruit/Adafruit_CircuitPython_AS7341
"""
from time import sleep

import board
from adafruit_as7341 import AS7341
from blinkt import clear, set_brightness, set_pixel, show

set_brightness(0.05)

clear()
set_pixel(0, 255, 255, 255)
show()

i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = AS7341(i2c)


def bar_graph(read_value):
    scaled = int(read_value / 1000)
    return "[%5d] " % read_value + (scaled * "*")


for _ in range(10):

    print("F1 - 415nm/Violet  %s" % bar_graph(sensor.channel_415nm))
    print("F2 - 445nm//Indigo %s" % bar_graph(sensor.channel_445nm))
    print("F3 - 480nm//Blue   %s" % bar_graph(sensor.channel_480nm))
    print("F4 - 515nm//Cyan   %s" % bar_graph(sensor.channel_515nm))
    print("F5 - 555nm/Green   %s" % bar_graph(sensor.channel_555nm))
    print("F6 - 590nm/Yellow  %s" % bar_graph(sensor.channel_590nm))
    print("F7 - 630nm/Orange  %s" % bar_graph(sensor.channel_630nm))
    print("F8 - 680nm/Red     %s" % bar_graph(sensor.channel_680nm))
    print("Clear              %s" % bar_graph(sensor.channel_clear))
    print("Near-IR (NIR)      %s" % bar_graph(sensor.channel_nir))
    print("\n------------------------------------------------")
    sleep(1)

clear()
show()

1 + 1
